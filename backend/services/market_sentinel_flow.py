"""
Market Sentinel multi-agent workflow orchestration.

Coordinates Azure AI Foundry agents to detect supply chain risks.
"""

import json
import logging
from typing import Any, Optional

from azure.ai.agents.models import MessageRole

from core.market_sentinel_agents import registry
from services.market_returns import compute_returns_snapshot

logger = logging.getLogger(__name__)


class MarketSentinelFlow:
    """
    Orchestrates the Market Sentinel multi-agent workflow.
    
    Flow:
    1. Watchlist Loader → Query Plan (P1)
    2. Bing Scout → Candidate Events Web (P2)
    3. GDELT Scout → Candidate Events API (P3)
    4. Returns Analyst → Returns Snapshot (P4)
    5. Evidence Judge → Sufficiency Verdict
    6. Decision Gate → Refine or Finalize
    7. Output → Signal Packet JSON
    """
    
    def __init__(self):
        self.client = registry.client
    
    async def run(
        self,
        watchlist: dict[str, Any],
        time_window_hours: int,
        sensitivity: Any,
        active_shipments_subset: Optional[list[str]] = None,
        returns_symbols: Optional[list[str]] = None,
        returns_days: int = 10,
    ) -> tuple[str, str]:
        """
        Execute the full Market Sentinel workflow.
        
        Args:
            watchlist: Watchlist configuration with lanes and entities
            time_window_hours: Time window for news search
            sensitivity: Sensitivity thresholds (min_severity, min_confidence)
            active_shipments_subset: Optional shipment IDs to focus on
            returns_symbols: Stock symbols for returns analysis
            returns_days: Days of historical returns
            
        Returns:
            Tuple of (thread_id, raw_text_output)
        """
        if returns_symbols is None:
            returns_symbols = ["^spx"]
        
        # Step 1: Compute market returns snapshot (P4)
        returns_snapshot = await self._compute_returns(returns_symbols, returns_days)
        
        # Step 2: Get or create all agents
        watchlist_loader = registry.get_or_create_watchlist_loader()
        bing_scout = registry.get_or_create_bing_scout()
        gdelt_scout = registry.get_or_create_gdelt_scout()
        judge_agent = registry.get_or_create_judge_agent()
        orchestrator = registry.get_or_create_orchestrator(
            watchlist_loader=watchlist_loader,
            bing_scout=bing_scout,
            gdelt_scout=gdelt_scout,
            judge_agent=judge_agent,
        )
        
        # Step 3: Create thread and send initial message
        thread = self.client.agents.threads.create()
        logger.info(f"Created thread: {thread.id}")
        
        user_message = self._build_orchestrator_prompt(
            watchlist=watchlist,
            time_window_hours=time_window_hours,
            sensitivity=sensitivity,
            active_shipments_subset=active_shipments_subset,
            returns_snapshot=returns_snapshot,
        )
        
        self.client.agents.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_message,
        )
        
        # Step 4: Run orchestrator
        run = self.client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=orchestrator.id,
        )
        
        logger.info(f"Run completed with status: {run.status}")
        
        if run.status != "completed":
            # Extract detailed error information - log all run attributes
            error_info = []
            for attr in ['last_error', 'incomplete_details', 'failed_at', 'required_action']:
                if hasattr(run, attr):
                    val = getattr(run, attr)
                    if val:
                        error_info.append(f"{attr}: {val}")
            
            # Also try to dump all public attributes
            try:
                run_attrs = {k: str(v)[:200] for k, v in vars(run).items() if not k.startswith('_')}
                logger.error(f"Run object attributes: {run_attrs}")
            except Exception:
                pass
            
            error_details = " | ".join(error_info) if error_info else "No additional error details"
            logger.error(f"Run failed: {run.status} - {error_details}")
            raise RuntimeError(f"Orchestrator run failed with status: {run.status} - {error_details}")
        
        # Step 5: Extract final response
        messages = self.client.agents.messages.list(thread_id=thread.id)
        
        assistant_messages = [
            msg for msg in messages 
            if msg.role == MessageRole.AGENT
        ]
        
        if not assistant_messages:
            raise RuntimeError("No assistant messages found in thread")
        
        last_message = assistant_messages[-1]
        raw_text = ""
        
        for content_block in last_message.content:
            if hasattr(content_block, "text") and content_block.text:
                raw_text += content_block.text.value
        
        logger.info(f"Raw output length: {len(raw_text)} chars")
        
        return thread.id, raw_text
    
    async def _compute_returns(
        self,
        symbols: list[str],
        days: int,
    ) -> list[dict[str, Any]]:
        """Compute market returns snapshot for given symbols."""
        snapshots = []
        
        for symbol in symbols:
            try:
                snapshot = compute_returns_snapshot(symbol, days)
                snapshots.append(snapshot.model_dump())
            except Exception as e:
                logger.warning(f"Failed to compute returns for {symbol}: {e}")
                snapshots.append({
                    "symbol": symbol,
                    "error": str(e),
                })
        
        return snapshots
    
    def _build_orchestrator_prompt(
        self,
        watchlist: dict[str, Any],
        time_window_hours: int,
        sensitivity: Any,
        active_shipments_subset: Optional[list[str]],
        returns_snapshot: list[dict[str, Any]],
    ) -> str:
        """Build a concise prompt for the orchestrator agent."""
        sensitivity_dict = sensitivity.model_dump() if hasattr(sensitivity, "model_dump") else dict(sensitivity)
        
        # Compact JSON without indentation to reduce tokens
        watchlist_compact = json.dumps(watchlist, separators=(',', ':'))
        
        # Simplify returns snapshot - only key metrics
        returns_summary = []
        for r in returns_snapshot:
            if 'error' not in r:
                returns_summary.append({
                    "symbol": r.get("symbol"),
                    "return_pct": r.get("return_pct"),
                    "trend": r.get("trend", "neutral")
                })
        
        prompt = f"""Watchlist: {watchlist_compact}
Config: time={time_window_hours}h, min_severity={sensitivity_dict.get('min_severity', 'MEDIUM')}, min_confidence={sensitivity_dict.get('min_confidence', 0.6)}
Returns: {json.dumps(returns_summary, separators=(',', ':'))}

Execute workflow: watchlist_loader→bing_scout+gdelt_scout→judge_agent→Signal Packet JSON."""
        
        return prompt

