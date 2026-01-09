"""
Market Sentinel API Routes - Azure AI Foundry Multi-Agent Workflow

Provides supply chain risk monitoring through multi-agent orchestration.
"""

import json
import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.market_sentinel_flow import MarketSentinelFlow
from services.market_sentinel_schemas import (
    SignalPacket,
    SensitivityConfig,
    MarketSentinelRequest,
    MarketSentinelResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/market-sentinel", tags=["Market Sentinel"])

# Global flow instance
_flow: Optional[MarketSentinelFlow] = None


def get_flow() -> MarketSentinelFlow:
    """Get or create the Market Sentinel flow instance."""
    global _flow
    if _flow is None:
        _flow = MarketSentinelFlow()
    return _flow


@router.get("/health")
async def health_check():
    """Health check endpoint for Market Sentinel service."""
    from config import get_settings
    settings = get_settings()
    
    return {
        "service": "market-sentinel",
        "status": "healthy",
        "azure_foundry_project_endpoint_configured": bool(settings.azure_foundry_project_endpoint),
        "bing_connection_configured": bool(settings.azure_bing_connection_id),
    }


@router.post("/run", response_model=MarketSentinelResponse)
async def run_market_sentinel(request: MarketSentinelRequest) -> MarketSentinelResponse:
    """
    Execute the Market Sentinel multi-agent workflow.
    
    This endpoint orchestrates multiple Azure AI Foundry agents to:
    1. Load watchlist and shipment data
    2. Search web for relevant news (Bing Grounding)
    3. Query GDELT news API
    4. Compute market returns snapshot
    5. Judge evidence sufficiency
    6. Produce final Signal Packet
    
    **Workflow:**
    - Watchlist Loader → Query Plan (P1)
    - Bing Scout → Candidate Events Web (P2)
    - GDELT Scout → Candidate Events API (P3)
    - Returns Analyst → Returns Snapshot (P4)
    - Evidence Judge → Sufficiency verdict
    - Decision Gate → Refine once if insufficient, else finalize
    
    **Example Request:**
    ```json
    {
        "watchlist": {
            "lanes": [
                {"origin": "CNSHA", "destination": "USLAX", "commodities": ["electronics"]}
            ],
            "entities": ["Port of Shanghai", "COSCO"]
        },
        "time_window_hours": 24,
        "sensitivity": {"min_severity": "MEDIUM", "min_confidence": 0.6}
    }
    ```
    """
    flow = get_flow()
    
    try:
        thread_id, raw_text = await flow.run(
            watchlist=request.watchlist,
            time_window_hours=request.time_window_hours,
            sensitivity=request.sensitivity,
            active_shipments_subset=request.active_shipments_subset,
            returns_symbols=request.returns_symbols,
            returns_days=request.returns_days,
        )
    except Exception as e:
        logger.exception("Market Sentinel flow failed")
        raise HTTPException(status_code=500, detail=f"Flow execution failed: {str(e)}")
    
    # Parse and validate Signal Packet
    signal_packet = _parse_signal_packet(raw_text, attempt=1)
    
    if signal_packet is None:
        logger.warning("First JSON parse failed, retrying flow once")
        try:
            thread_id, raw_text = await flow.run(
                watchlist=request.watchlist,
                time_window_hours=request.time_window_hours,
                sensitivity=request.sensitivity,
                active_shipments_subset=request.active_shipments_subset,
                returns_symbols=request.returns_symbols,
                returns_days=request.returns_days,
            )
            signal_packet = _parse_signal_packet(raw_text, attempt=2)
        except Exception as e:
            logger.exception("Retry flow failed")
            raise HTTPException(
                status_code=500,
                detail=f"Flow retry failed: {str(e)}",
            )
    
    if signal_packet is None:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse valid Signal Packet JSON after retry. Raw output: {raw_text[:1000]}",
        )
    
    return MarketSentinelResponse(
        thread_id=thread_id,
        signal_packet=signal_packet,
        raw_text=raw_text,
        request_echo=request.model_dump(),
    )


@router.post("/run/simple")
async def run_market_sentinel_simple(
    watchlist_lanes: list[dict] = None,
    watchlist_entities: list[str] = None,
    time_window_hours: int = 24,
    min_confidence: float = 0.6,
):
    """
    Simplified Market Sentinel endpoint with query parameters.
    
    This is a convenience endpoint for quick testing without full JSON body.
    
    Args:
        watchlist_lanes: List of lane dicts with origin/destination/commodities
        watchlist_entities: List of entity names to monitor
        time_window_hours: Hours to look back for news
        min_confidence: Minimum confidence threshold
    """
    # Build default watchlist if not provided
    watchlist = {
        "lanes": watchlist_lanes or [
            {"origin": "CNSHA", "destination": "USLAX", "commodities": ["electronics", "semiconductors"]},
        ],
        "entities": watchlist_entities or ["Port of Shanghai", "Port of Los Angeles"],
    }
    
    request = MarketSentinelRequest(
        watchlist=watchlist,
        time_window_hours=time_window_hours,
        sensitivity=SensitivityConfig(min_confidence=min_confidence),
    )
    
    return await run_market_sentinel(request)


@router.get("/agents/status")
async def get_agents_status():
    """
    Get status of registered Azure AI Foundry agents.
    
    Returns the cached agent IDs and their status.
    """
    from core.market_sentinel_agents import registry
    
    agents = {}
    for name, agent in registry._agents.items():
        agents[name] = {
            "id": agent.id,
            "name": agent.name,
            "model": agent.model,
        }
    
    return {
        "total_agents": len(agents),
        "agents": agents,
        "client_initialized": registry._client is not None,
    }


@router.delete("/agents/cleanup")
async def cleanup_agents():
    """
    Delete all cached agents from Azure AI Foundry.
    
    Use this to reset agent state or when updating agent configurations.
    """
    from core.market_sentinel_agents import registry
    
    count = len(registry._agents)
    registry.cleanup_agents()
    
    return {
        "message": f"Cleaned up {count} agents",
        "agents_remaining": len(registry._agents),
    }


def _parse_signal_packet(raw_text: str, attempt: int) -> Optional[SignalPacket]:
    """
    Parse and validate Signal Packet JSON from raw agent output.
    
    Handles common issues like markdown code fences.
    """
    text = raw_text.strip()
    
    # Remove markdown code fences if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]
    
    text = text.strip()
    
    try:
        data = json.loads(text)
        signal_packet = SignalPacket.model_validate(data)
        logger.info(f"Successfully parsed Signal Packet on attempt {attempt}")
        return signal_packet
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error on attempt {attempt}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Validation error on attempt {attempt}: {e}")
        return None

