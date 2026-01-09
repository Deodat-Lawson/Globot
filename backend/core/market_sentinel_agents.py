"""
Azure AI Foundry Agent Registry for Market Sentinel.

Caches agent IDs to avoid recreation on every request.
"""

import logging
from typing import Optional

from azure.ai.projects import AIProjectClient
from azure.core.pipeline.policies import RetryPolicy
from azure.ai.agents.models import (
    Agent,
    BingGroundingTool,
    OpenApiTool,
    OpenApiAnonymousAuthDetails,
    ConnectedAgentTool,
    ToolSet,
)
from azure.identity import DefaultAzureCredential
import jsonref

from config import get_settings
from core.market_sentinel_tools import get_gdelt_openapi_spec

logger = logging.getLogger(__name__)


class FoundryAgentRegistry:
    """
    In-process registry that caches Azure AI Foundry agent IDs.
    
    Prevents agent recreation on every request by storing agent references.
    Implements singleton pattern for global access.
    """
    
    _instance: Optional["FoundryAgentRegistry"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "FoundryAgentRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._client: Optional[AIProjectClient] = None
        self._agents: dict[str, Agent] = {}
        self._initialized = True
    
    @property
    def client(self) -> AIProjectClient:
        """Get or create the AI Project Client."""
        if self._client is None:
            settings = get_settings()
            
            if not settings.azure_foundry_project_endpoint:
                raise ValueError("azure_foundry_project_endpoint is not configured. Set AZURE_FOUNDRY_PROJECT_ENDPOINT env var.")
            
            self._client = AIProjectClient(
                endpoint=settings.azure_foundry_project_endpoint,
                credential=DefaultAzureCredential(),
                retry_policy=RetryPolicy(retry_total=2, retry_backoff_factor=0.5),
                connection_timeout=30,
                read_timeout=180,  # 3 minutes for agent operations
            )
            logger.info(f"Created AIProjectClient for endpoint: {settings.azure_foundry_project_endpoint[:50]}...")
        
        return self._client
    
    def get_or_create_watchlist_loader(self) -> Agent:
        """Get or create the Watchlist Loader agent (no external API - processes data from prompt)."""
        agent_key = "watchlist_loader"
        
        if agent_key in self._agents:
            logger.debug(f"Returning cached agent: {agent_key}")
            return self._agents[agent_key]
        
        settings = get_settings()
        
        # No external API tool - watchlist data is passed directly in the prompt
        instructions = """Analyze watchlist and output JSON query plan:
{"query_plan":{"lanes":[{"origin":"CODE","destination":"CODE","commodities":["item"]}],"entities":["entity"],"search_keywords":["keyword"],"time_window_hours":24},"watchlist_summary":"brief summary"}"""
        
        agent = self.client.agents.create_agent(
            model=settings.azure_foundry_model,
            name="watchlist_loader",
            instructions=instructions,
            tools=[],  # No external tools needed
        )
        
        self._agents[agent_key] = agent
        logger.info(f"Created agent: {agent_key} with ID: {agent.id}")
        return agent
    
    def get_or_create_bing_scout(self) -> Agent:
        """Get or create the Bing Scout agent with Bing Grounding tool."""
        agent_key = "bing_scout"
        
        if agent_key in self._agents:
            logger.debug(f"Returning cached agent: {agent_key}")
            return self._agents[agent_key]
        
        settings = get_settings()
        
        if not settings.azure_bing_connection_id:
            raise ValueError("azure_bing_connection_id is not configured. Set AZURE_BING_CONNECTION_ID env var.")
        
        bing_tool = BingGroundingTool(connection_id=settings.azure_bing_connection_id)
        
        # Create ToolSet for proper SDK integration
        toolset = ToolSet()
        toolset.add(bing_tool)
        
        instructions = """Search web for supply chain risks (port delays, weather, strikes, incidents). Return JSON:
{"candidate_events":[{"headline":"...","summary":"...","url":"...","event_type":"disruption|weather|labor|incident"}],"total_results_scanned":0}"""
        
        agent = self.client.agents.create_agent(
            model=settings.azure_foundry_model,
            name="bing_scout",
            instructions=instructions,
            toolset=toolset,
        )
        
        self._agents[agent_key] = agent
        logger.info(f"Created agent: {agent_key} with ID: {agent.id}")
        return agent
    
    def get_or_create_gdelt_scout(self) -> Agent:
        """Get or create the GDELT Scout agent with OpenAPI tool."""
        agent_key = "gdelt_scout"
        
        if agent_key in self._agents:
            logger.debug(f"Returning cached agent: {agent_key}")
            return self._agents[agent_key]
        
        settings = get_settings()
        spec = get_gdelt_openapi_spec()
        resolved_spec = jsonref.JsonRef.replace_refs(spec)
        
        openapi_tool = OpenApiTool(
            name="gdelt_api",
            description="GDELT DOC API for querying global news events",
            spec=resolved_spec,
            auth=OpenApiAnonymousAuthDetails(),
        )
        
        # Create ToolSet for proper SDK integration
        toolset = ToolSet()
        toolset.add(openapi_tool)
        
        instructions = """Query GDELT for supply chain news. Use boolean queries like: (port OR shipping) AND delay. Return JSON:
{"candidate_events":[{"headline":"...","summary":"...","url":"...","event_type":"disruption|weather|labor"}],"total_articles_found":0}"""
        
        agent = self.client.agents.create_agent(
            model=settings.azure_foundry_model,
            name="gdelt_scout",
            instructions=instructions,
            toolset=toolset,
        )
        
        self._agents[agent_key] = agent
        logger.info(f"Created agent: {agent_key} with ID: {agent.id}")
        return agent
    
    def get_or_create_judge_agent(self) -> Agent:
        """Get or create the Evidence Judge agent."""
        agent_key = "judge_agent"
        
        if agent_key in self._agents:
            logger.debug(f"Returning cached agent: {agent_key}")
            return self._agents[agent_key]
        
        settings = get_settings()
        
        instructions = """Evaluate evidence from web/news searches. Check source count, agreement, recency. Return JSON:
{"verdict":"sufficient|insufficient","confidence_score":0.0,"merged_events":[{"headline":"...","summary":"...","severity_estimate":"LOW|MEDIUM|HIGH|CRITICAL"}]}"""
        
        agent = self.client.agents.create_agent(
            model=settings.azure_foundry_model,
            name="judge_agent",
            instructions=instructions,
            tools=[],
        )
        
        self._agents[agent_key] = agent
        logger.info(f"Created agent: {agent_key} with ID: {agent.id}")
        return agent
    
    def get_or_create_orchestrator(
        self,
        watchlist_loader: Agent,
        bing_scout: Agent,
        gdelt_scout: Agent,
        judge_agent: Agent,
    ) -> Agent:
        """Get or create the Orchestrator agent with ConnectedAgentTools."""
        agent_key = "orchestrator"
        
        if agent_key in self._agents:
            logger.debug(f"Returning cached agent: {agent_key}")
            return self._agents[agent_key]
        
        settings = get_settings()
        
        # Create connected agent tools
        connected_watchlist = ConnectedAgentTool(
            id=watchlist_loader.id,
            name="watchlist_loader",
            description="Loads watchlist and shipment data, returns Query Plan",
        )
        
        connected_bing = ConnectedAgentTool(
            id=bing_scout.id,
            name="bing_scout",
            description="Searches web for supply chain events using Bing",
        )
        
        connected_gdelt = ConnectedAgentTool(
            id=gdelt_scout.id,
            name="gdelt_scout",
            description="Queries GDELT news API for supply chain events",
        )
        
        connected_judge = ConnectedAgentTool(
            id=judge_agent.id,
            name="judge_agent",
            description="Evaluates evidence sufficiency and merges events",
        )
        
        # Get tool definitions for API serialization
        # ToolSet doesn't support multiple tools of same type, so we extract definitions
        tools_list = (
            connected_watchlist.definitions +
            connected_bing.definitions +
            connected_gdelt.definitions +
            connected_judge.definitions
        )
        
        instructions = """Orchestrator for supply chain risk detection. 

FLOW: watchlist_loader→bing_scout→gdelt_scout→judge_agent→output JSON

OUTPUT (JSON only):
{"signal_id":"SIG-YYYY-MM-DD-XXXXX","timestamp_utc":"ISO8601","summary":"...","affected_lanes":[{"origin":"CODE","destination":"CODE","risk":"low|medium|high"}],"entities":[{"name":"...","type":"organization|port|country|vessel|commodity"}],"severity":"LOW|MEDIUM|HIGH|CRITICAL","expected_horizon_days":0,"citations":[{"title":"...","url":"..."}],"confidence":0.0}"""
        
        agent = self.client.agents.create_agent(
            model=settings.azure_foundry_model,
            name="orchestrator",
            instructions=instructions,
            tools=tools_list,
        )
        
        self._agents[agent_key] = agent
        logger.info(f"Created agent: {agent_key} with ID: {agent.id}")
        return agent
    
    def cleanup_agents(self) -> None:
        """Delete all cached agents from Azure AI Foundry."""
        for agent_key, agent in self._agents.items():
            try:
                self.client.agents.delete_agent(agent.id)
                logger.info(f"Deleted agent: {agent_key} with ID: {agent.id}")
            except Exception as e:
                logger.warning(f"Failed to delete agent {agent_key}: {e}")
        
        self._agents.clear()


# Global singleton instance
registry = FoundryAgentRegistry()

