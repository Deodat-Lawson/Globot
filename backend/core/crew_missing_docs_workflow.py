"""
CrewAI Workflow for Missing Document Detection
Dedicated 2-agent system that compares a vessel's existing documents against
route requirements to identify gaps, expired docs, and compliance issues.

Unlike crew_document_agents.py which analyzes raw uploaded document content (OCR text),
this workflow operates on already-processed structured UserDocument records
and focuses purely on gap detection against a specific route.
"""
import os
import json
import logging
from typing import List, Optional, Dict, Any, Tuple

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Try to import CrewAI
try:
    from crewai import Agent, Task, Crew, LLM
    HAS_CREWAI = True
except ImportError:
    HAS_CREWAI = False
    logger.warning("crewai not found. Missing docs workflow will not be available.")


def _test_gemini_connection(api_key: str, timeout: int = 10) -> None:
    """Test Google Gemini connection before initializing crew"""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        model.generate_content("ping", request_options={"timeout": timeout})
    except Exception as e:
        raise RuntimeError(f"Gemini health check failed: {type(e).__name__}: {e}") from e


MISSING_DOCS_RULES = """You MUST follow these rules for missing document detection:
1) Consider vessel type, flag state, and gross tonnage for regulation applicability
2) Check EVERY port on the route for port-specific document requirements
3) Cross-reference the vessel's existing documents against the full requirement set
4) Flag expired and expiring-soon (<30 days) documents as effectively "missing"
5) Prioritize findings: CRITICAL (voyage-blocking), HIGH (PSC detention risk), MEDIUM (advisory)
6) Always provide actionable recommendations with specific next steps
7) Output must be valid JSON when structured data is requested
Keep outputs focused and actionable for ship operators.
"""


def _init_llm():
    """Initialize LLM for CrewAI - uses Google Gemini by default"""
    if not HAS_CREWAI:
        raise RuntimeError("CrewAI not installed")

    # Try Google Gemini first (preferred)
    if settings.google_api_key:
        os.environ.setdefault("GOOGLE_API_KEY", settings.google_api_key)
        _test_gemini_connection(api_key=settings.google_api_key)
        return LLM(
            model="gemini/gemini-2.0-flash",
            api_key=settings.google_api_key
        )

    # Fall back to OpenAI if configured
    if settings.openai_api_key:
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
        if settings.openai_base_url:
            os.environ.setdefault("OPENAI_BASE_URL", settings.openai_base_url)
        model_name = settings.openai_model or "gpt-4o-mini"
        return LLM(model=model_name)

    raise RuntimeError("No LLM API key configured. Set GOOGLE_API_KEY or OPENAI_API_KEY.")


def build_missing_docs_crew(
    vessel_info: Dict[str, Any],
    route_ports: List[str],
    existing_documents: List[Dict[str, Any]]
) -> Tuple[Any, List[Any]]:
    """
    Build a focused 2-agent CrewAI crew for missing document detection.

    Args:
        vessel_info: Dict with vessel details (name, imo_number, vessel_type, flag_state, gross_tonnage)
        route_ports: List of port codes in route order
        existing_documents: List of dicts with structured document data from DB
            [{"document_type": "...", "expiry_date": "...", "is_expired": bool, ...}, ...]

    Returns:
        Tuple of (Crew, List[Task])
    """
    if not HAS_CREWAI:
        raise RuntimeError("CrewAI not installed. Cannot build missing docs crew.")

    from core.document_tools import get_document_tools

    llm = _init_llm()
    tools = get_document_tools()

    common_backstory = (
        "You are part of a maritime compliance team specializing in "
        "document gap detection and regulatory compliance verification.\n"
        + MISSING_DOCS_RULES
    )

    # Format inputs
    vessel_str = json.dumps(vessel_info, indent=2)
    route_str = " -> ".join(route_ports)
    existing_docs_summary = json.dumps(existing_documents, indent=2)

    # ========== AGENTS ==========

    route_requirements_analyst = Agent(
        role="Route Requirements Analyst",
        goal="Identify ALL documents required for the vessel's route across every port",
        backstory=common_backstory + "\nYou are an expert on maritime regulatory requirements. "
                  "You know exactly which certificates and documents are required for different "
                  "vessel types, flag states, and port destinations. You systematically check "
                  "IMO conventions, port state control requirements, regional regulations, "
                  "and port-specific rules for every port on the route.",
        llm=llm,
        tools=tools,
        verbose=True,
    )

    gap_detector = Agent(
        role="Document Gap Detector",
        goal="Compare the vessel's existing documents against route requirements and identify all gaps",
        backstory=common_backstory + "\nYou excel at document gap detection. "
                  "You compare what a vessel has on file against what is required, "
                  "identifying missing documents, expired certificates, and documents expiring soon. "
                  "You provide prioritized, actionable recommendations for achieving full compliance.",
        llm=llm,
        tools=tools,
        verbose=True,
    )

    # ========== TASKS ==========

    tasks: List[Task] = []

    # Task 1: Determine all required documents for the route
    tasks.append(Task(
        description=f"""
Determine ALL documents required for this vessel's voyage.

VESSEL INFORMATION:
{vessel_str}

ROUTE: {route_str}

Use the requirements_lookup tool to find all required documents based on:
1. Vessel type: {vessel_info.get('vessel_type', 'container')}
2. Flag state: {vessel_info.get('flag_state', 'Unknown')}
3. Destination ports: {route_ports}

Include:
1. Mandatory IMO convention certificates (SOLAS, MARPOL, ISM, ISPS, Load Line, Tonnage, Registry)
2. Port-specific requirements for each destination port
3. Regional requirements (EU MRV if applicable, ECA compliance)
4. Flag state specific requirements

Output as JSON:
{{
  "context": {{
    "vessel_type": "...",
    "flag_state": "...",
    "ports": [...]
  }},
  "required_documents": [
    {{
      "document_type": "...",
      "requirement_source": "IMO/Port/Regional",
      "mandatory": true/false,
      "applies_to_ports": ["ALL"] or ["SGSIN", "NLRTM"]
    }}
  ],
  "total_required": int
}}

Limit: 400 words.
""",
        agent=route_requirements_analyst,
        expected_output="JSON with complete list of required documents for the route"
    ))

    # Task 2: Compare existing documents against requirements and detect gaps
    tasks.append(Task(
        description=f"""
Compare the vessel's existing documents against the requirements from the previous analysis to detect all gaps.

VESSEL'S EXISTING DOCUMENTS ON FILE:
{existing_docs_summary}

Each document has: document_type, expiry_date, is_expired, is_validated, document_number, issuing_authority, title.

Use the document_comparison tool with:
- user_documents_json: The existing documents listed above
- required_documents_json: The required document types from the previous task

Produce a comprehensive gap analysis:

1. VALID DOCUMENTS - Present, not expired
2. EXPIRING SOON (within 30 days) - Need renewal soon
3. EXPIRED DOCUMENTS - Have expired, urgency CRITICAL
4. MISSING DOCUMENTS - Required but not on file
5. COMPLIANCE SCORE - Overall percentage
6. PRIORITIZED RECOMMENDATIONS - Ranked by priority

Output as JSON:
{{
  "overall_status": "COMPLIANT|PARTIAL|NON_COMPLIANT",
  "compliance_score": 0-100,
  "summary": "1-2 sentence summary",
  "valid_documents": [
    {{
      "document_type": "...",
      "expiry_date": "YYYY-MM-DD",
      "status": "valid",
      "days_until_expiry": int
    }}
  ],
  "expiring_soon": [
    {{
      "document_type": "...",
      "expiry_date": "YYYY-MM-DD",
      "status": "expiring_soon",
      "days_until_expiry": int
    }}
  ],
  "expired_documents": [
    {{
      "document_type": "...",
      "expiry_date": "YYYY-MM-DD",
      "status": "expired",
      "days_until_expiry": int
    }}
  ],
  "missing_documents": [
    {{
      "document_type": "...",
      "required_by": ["regulation or port"],
      "priority": "CRITICAL|HIGH|MEDIUM"
    }}
  ],
  "recommendations": [
    {{
      "priority": "CRITICAL|HIGH|MEDIUM",
      "action": "...",
      "documents": ["..."],
      "deadline": "immediate|within_30_days|before_voyage"
    }}
  ]
}}

Limit: 600 words.
""",
        agent=gap_detector,
        expected_output="JSON gap analysis report with missing documents and recommendations"
    ))

    # Create Crew
    crew = Crew(
        agents=[route_requirements_analyst, gap_detector],
        tasks=tasks,
        verbose=True
    )

    return crew, tasks


async def run_missing_docs_detection(
    vessel_info: Dict[str, Any],
    route_ports: List[str],
    existing_documents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Run the missing documents detection workflow using CrewAI.

    Args:
        vessel_info: Vessel information dict
        route_ports: List of port codes
        existing_documents: List of structured document data from DB

    Returns:
        Dict with detection results and agent outputs
    """
    if not HAS_CREWAI:
        return {
            "error": "CrewAI not installed",
            "mock_result": True,
            "success": False,
            "overall_status": "PENDING_REVIEW",
            "message": "Missing docs detection requires CrewAI to be installed"
        }

    if not settings.document_analysis_use_crewai:
        return {
            "error": "CrewAI document analysis is disabled",
            "mock_result": True,
            "success": False,
            "overall_status": "PENDING_REVIEW",
            "message": "Enable document_analysis_use_crewai in settings"
        }

    try:
        crew, tasks = build_missing_docs_crew(
            vessel_info=vessel_info,
            route_ports=route_ports,
            existing_documents=existing_documents
        )

        # Run the crew
        result = crew.kickoff()

        # Try to parse the final result as JSON
        parsed_result = None
        try:
            result_str = str(result)
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                parsed_result = json.loads(result_str[json_start:json_end])
        except json.JSONDecodeError:
            parsed_result = None

        return {
            "success": True,
            "crew_output": str(result),
            "parsed_result": parsed_result,
            "tasks_completed": len(tasks),
            "documents_on_file": len(existing_documents),
            "vessel_info": vessel_info,
            "route_ports": route_ports
        }

    except Exception as e:
        logger.error(f"Missing docs detection crew error: {e}")
        return {
            "error": str(e),
            "success": False,
            "overall_status": "ERROR"
        }


class MissingDocsOrchestrator:
    """
    Orchestrator for the missing documents detection workflow.
    Provides singleton pattern and manages the detection workflow.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._available = HAS_CREWAI and settings.document_analysis_use_crewai

    @property
    def is_available(self) -> bool:
        return self._available

    async def detect_missing_documents(
        self,
        vessel_info: Dict[str, Any],
        route_ports: List[str],
        existing_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run missing documents detection"""
        return await run_missing_docs_detection(
            vessel_info=vessel_info,
            route_ports=route_ports,
            existing_documents=existing_documents
        )


def get_missing_docs_orchestrator() -> MissingDocsOrchestrator:
    """Get singleton orchestrator instance"""
    return MissingDocsOrchestrator()
