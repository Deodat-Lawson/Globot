"""
Maritime Compliance API Routes
Endpoints for vessel management, document upload, and compliance checking
"""
import logging
import json
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Vessel, UserDocument, Port, VesselType, DocumentType
)
from services.document_service import DocumentService
from services.compliance_service import ComplianceService
from services.maritime_knowledge_base import get_maritime_knowledge_base
from services.compliance_report_generator import get_compliance_report_generator
from core.crew_maritime_compliance import get_compliance_orchestrator
from core.crew_document_agents import get_document_analysis_orchestrator
from models.compliance_report import (
    ComplianceReport,
    ComplianceStatus,
    Priority,
    RiskLevel,
    QuickComplianceCheck,
    RegulationQueryResponse,
    PortQueryResponse,
    ActionItem,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/maritime", tags=["Maritime Compliance"])


# ========== Request/Response Models ==========

class VesselCreate(BaseModel):
    """Request model for creating a vessel"""
    name: str = Field(..., min_length=1, max_length=200)
    imo_number: str = Field(..., pattern=r"^\d{7}$", description="7-digit IMO number")
    vessel_type: VesselType
    flag_state: str = Field(..., min_length=2, max_length=100)
    gross_tonnage: float = Field(..., gt=0)
    mmsi: Optional[str] = None
    call_sign: Optional[str] = None
    dwt: Optional[float] = None
    year_built: Optional[int] = None
    classification_society: Optional[str] = None


class VesselResponse(BaseModel):
    """Response model for vessel"""
    id: int
    name: str
    imo_number: str
    vessel_type: str
    flag_state: str
    gross_tonnage: float
    mmsi: Optional[str]
    call_sign: Optional[str]
    dwt: Optional[float]
    year_built: Optional[int]
    classification_society: Optional[str]
    document_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Response model for document"""
    id: int
    title: str
    document_type: str
    file_name: Optional[str]
    file_size: Optional[int]
    ocr_confidence: Optional[float]
    issuing_authority: Optional[str]
    issue_date: Optional[datetime]
    expiry_date: Optional[datetime]
    document_number: Optional[str]
    is_validated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RouteComplianceRequest(BaseModel):
    """Request model for route compliance check"""
    vessel_id: int
    port_codes: List[str] = Field(..., min_length=1, description="List of UN/LOCODE port codes")
    route_name: Optional[str] = None
    use_crewai: bool = Field(default=False, description="Use CrewAI for comprehensive analysis")


class PortComplianceResponse(BaseModel):
    """Response model for port compliance"""
    port_code: str
    port_name: str
    status: str
    required_documents: List[dict]
    missing_documents: List[dict]
    expired_documents: List[dict]
    special_requirements: List[str]
    risk_factors: List[str]


class RouteComplianceResponse(BaseModel):
    """Response model for route compliance"""
    check_id: Optional[int] = None
    vessel_id: int
    route_name: str
    route_ports: List[str]
    overall_status: str
    compliance_score: float
    port_results: List[PortComplianceResponse]
    missing_documents: List[dict]
    recommendations: List[str]
    risk_level: str
    summary_report: str
    detailed_report: Optional[str] = None


class KBSearchRequest(BaseModel):
    """Request model for knowledge base search"""
    query: str = Field(..., min_length=3)
    filters: Optional[dict] = None
    top_k: int = Field(default=5, ge=1, le=20)
    collections: Optional[List[str]] = None


class KBSearchResponse(BaseModel):
    """Response model for knowledge base search"""
    results: List[dict]
    query: str
    total_found: int


class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis with CrewAI agents"""
    vessel_id: int
    port_codes: List[str] = Field(..., min_length=1, description="List of UN/LOCODE port codes")
    document_ids: Optional[List[int]] = Field(None, description="Specific document IDs to analyze (default: all vessel docs)")


class DocumentSummary(BaseModel):
    """Summary of a document"""
    document_type: str
    expiry_date: Optional[str] = None
    status: str  # valid, expired, expiring_soon
    days_until_expiry: Optional[int] = None


class MissingDocument(BaseModel):
    """Missing document info"""
    document_type: str
    required_by: List[str]  # Regulations or ports requiring it
    priority: str  # CRITICAL, HIGH, MEDIUM


class Recommendation(BaseModel):
    """Recommendation from analysis"""
    priority: str  # CRITICAL, HIGH, MEDIUM
    action: str
    documents: List[str]
    deadline: Optional[str] = None


class DocumentAnalysisResponse(BaseModel):
    """Response model for document analysis"""
    success: bool
    overall_status: str  # COMPLIANT, PARTIAL, NON_COMPLIANT, ERROR
    compliance_score: int = Field(ge=0, le=100)
    documents_analyzed: int
    valid_documents: List[DocumentSummary]
    expiring_soon_documents: List[DocumentSummary]
    expired_documents: List[DocumentSummary]
    missing_documents: List[MissingDocument]
    recommendations: List[Recommendation]
    agent_reasoning: Optional[str] = None
    vessel_info: dict
    route_ports: List[str]


# ========== Vessel Management Endpoints ==========

@router.post("/vessels", response_model=VesselResponse, status_code=201)
async def create_vessel(
    vessel: VesselCreate,
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """Register a new vessel"""
    # Check for duplicate IMO number
    existing = db.query(Vessel).filter(Vessel.imo_number == vessel.imo_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vessel with this IMO number already exists")

    new_vessel = Vessel(
        customer_id=customer_id,
        name=vessel.name,
        imo_number=vessel.imo_number,
        vessel_type=vessel.vessel_type,
        flag_state=vessel.flag_state,
        gross_tonnage=vessel.gross_tonnage,
        mmsi=vessel.mmsi,
        call_sign=vessel.call_sign,
        dwt=vessel.dwt,
        year_built=vessel.year_built,
        classification_society=vessel.classification_society,
    )

    db.add(new_vessel)
    db.commit()
    db.refresh(new_vessel)

    return VesselResponse(
        id=new_vessel.id,
        name=new_vessel.name,
        imo_number=new_vessel.imo_number,
        vessel_type=new_vessel.vessel_type.value if new_vessel.vessel_type else None,
        flag_state=new_vessel.flag_state,
        gross_tonnage=new_vessel.gross_tonnage,
        mmsi=new_vessel.mmsi,
        call_sign=new_vessel.call_sign,
        dwt=new_vessel.dwt,
        year_built=new_vessel.year_built,
        classification_society=new_vessel.classification_society,
        document_count=0,
        created_at=new_vessel.created_at,
    )


@router.get("/vessels", response_model=List[VesselResponse])
async def list_vessels(
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """List all vessels for a customer"""
    vessels = db.query(Vessel).filter(Vessel.customer_id == customer_id).all()

    results = []
    for v in vessels:
        doc_count = db.query(UserDocument).filter(UserDocument.vessel_id == v.id).count()
        results.append(VesselResponse(
            id=v.id,
            name=v.name,
            imo_number=v.imo_number,
            vessel_type=v.vessel_type.value if v.vessel_type else None,
            flag_state=v.flag_state,
            gross_tonnage=v.gross_tonnage,
            mmsi=v.mmsi,
            call_sign=v.call_sign,
            dwt=v.dwt,
            year_built=v.year_built,
            classification_society=v.classification_society,
            document_count=doc_count,
            created_at=v.created_at,
        ))

    return results


@router.get("/vessels/{vessel_id}", response_model=VesselResponse)
async def get_vessel(vessel_id: int, db: Session = Depends(get_db)):
    """Get vessel details"""
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")

    doc_count = db.query(UserDocument).filter(UserDocument.vessel_id == vessel_id).count()

    return VesselResponse(
        id=vessel.id,
        name=vessel.name,
        imo_number=vessel.imo_number,
        vessel_type=vessel.vessel_type.value if vessel.vessel_type else None,
        flag_state=vessel.flag_state,
        gross_tonnage=vessel.gross_tonnage,
        mmsi=vessel.mmsi,
        call_sign=vessel.call_sign,
        dwt=vessel.dwt,
        year_built=vessel.year_built,
        classification_society=vessel.classification_society,
        document_count=doc_count,
        created_at=vessel.created_at,
    )


# ========== Document Upload Endpoints ==========

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    customer_id: int = Form(...),
    vessel_id: int = Form(...),
    document_type: DocumentType = Form(...),
    title: str = Form(...),
    issue_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    document_number: Optional[str] = Form(None),
    issuing_authority: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document (certificate, permit) with OCR processing.
    Supported formats: PDF, PNG, JPG
    """
    # Validate vessel exists
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")

    # Parse dates
    parsed_issue_date = None
    parsed_expiry_date = None

    if issue_date:
        try:
            parsed_issue_date = datetime.fromisoformat(issue_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid issue_date format. Use ISO format.")

    if expiry_date:
        try:
            parsed_expiry_date = datetime.fromisoformat(expiry_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiry_date format. Use ISO format.")

    # Upload document
    doc_service = DocumentService(db)

    try:
        document = await doc_service.upload_document(
            customer_id=customer_id,
            vessel_id=vessel_id,
            file=file,
            document_type=document_type,
            title=title,
            issue_date=parsed_issue_date,
            expiry_date=parsed_expiry_date,
            document_number=document_number,
            issuing_authority=issuing_authority,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return DocumentResponse(
        id=document.id,
        title=document.title,
        document_type=document.document_type.value,
        file_name=document.file_name,
        file_size=document.file_size,
        ocr_confidence=document.ocr_confidence,
        issuing_authority=document.issuing_authority,
        issue_date=document.issue_date,
        expiry_date=document.expiry_date,
        document_number=document.document_number,
        is_validated=document.is_validated,
        created_at=document.created_at,
    )


@router.get("/documents/vessel/{vessel_id}", response_model=List[DocumentResponse])
async def get_vessel_documents(
    vessel_id: int,
    document_type: Optional[DocumentType] = None,
    db: Session = Depends(get_db)
):
    """Get all documents for a vessel"""
    doc_service = DocumentService(db)
    documents = doc_service.get_vessel_documents(vessel_id, document_type)

    return [
        DocumentResponse(
            id=d.id,
            title=d.title,
            document_type=d.document_type.value,
            file_name=d.file_name,
            file_size=d.file_size,
            ocr_confidence=d.ocr_confidence,
            issuing_authority=d.issuing_authority,
            issue_date=d.issue_date,
            expiry_date=d.expiry_date,
            document_number=d.document_number,
            is_validated=d.is_validated,
            created_at=d.created_at,
        )
        for d in documents
    ]


@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document details including extracted text"""
    doc_service = DocumentService(db)
    document = doc_service.get_document(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": document.id,
        "title": document.title,
        "document_type": document.document_type.value,
        "file_name": document.file_name,
        "file_size": document.file_size,
        "mime_type": document.mime_type,
        "ocr_confidence": document.ocr_confidence,
        "extracted_text": document.extracted_text,
        "extracted_fields": json.loads(document.extracted_fields) if document.extracted_fields else {},
        "issuing_authority": document.issuing_authority,
        "issue_date": document.issue_date.isoformat() if document.issue_date else None,
        "expiry_date": document.expiry_date.isoformat() if document.expiry_date else None,
        "document_number": document.document_number,
        "is_validated": document.is_validated,
        "validation_notes": document.validation_notes,
        "created_at": document.created_at.isoformat(),
    }


@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    doc_service = DocumentService(db)
    success = doc_service.delete_document(document_id)

    if not success:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"status": "deleted", "document_id": document_id}


@router.post("/documents/analyze", response_model=DocumentAnalysisResponse)
async def analyze_documents_with_agents(
    request: DocumentAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze vessel documents using CrewAI agents.

    This endpoint runs a 3-agent crew:
    1. Document Analyzer - Classifies documents and extracts metadata
    2. Requirements Researcher - Determines required documents based on vessel/route
    3. Gap Analyst - Compares documents against requirements and provides recommendations

    Users upload documents first, then call this endpoint to get AI-driven analysis
    of what documents are present, missing, or expired.
    """
    # Validate vessel exists
    vessel = db.query(Vessel).filter(Vessel.id == request.vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")

    # Get orchestrator
    orchestrator = get_document_analysis_orchestrator()

    if not orchestrator.is_available:
        raise HTTPException(
            status_code=503,
            detail="Document analysis service not available. Check CrewAI configuration."
        )

    # Prepare vessel info
    vessel_info = {
        "name": vessel.name,
        "imo_number": vessel.imo_number,
        "vessel_type": vessel.vessel_type.value if vessel.vessel_type else "container",
        "flag_state": vessel.flag_state,
        "gross_tonnage": vessel.gross_tonnage,
    }

    # Get documents
    doc_service = DocumentService(db)

    if request.document_ids:
        # Get specific documents
        documents = []
        for doc_id in request.document_ids:
            doc = doc_service.get_document(doc_id)
            if doc and doc.vessel_id == request.vessel_id:
                documents.append(doc)
    else:
        # Get all vessel documents
        documents = doc_service.get_vessel_documents(request.vessel_id)

    if not documents:
        raise HTTPException(
            status_code=400,
            detail="No documents found for this vessel. Please upload documents first."
        )

    # Prepare document texts for analysis
    document_texts = [
        {
            "id": str(d.id),
            "filename": d.file_name or f"document_{d.id}",
            "file_type": d.mime_type or "application/pdf",
            "ocr_text": d.extracted_text or "",
            "document_type": d.document_type.value if d.document_type else "unknown",
            "expiry_date": d.expiry_date.strftime("%Y-%m-%d") if d.expiry_date else None,
        }
        for d in documents
    ]

    # Run CrewAI analysis
    result = await orchestrator.analyze_documents(
        document_texts=document_texts,
        vessel_info=vessel_info,
        route_ports=request.port_codes
    )

    if not result.get("success"):
        return DocumentAnalysisResponse(
            success=False,
            overall_status="ERROR",
            compliance_score=0,
            documents_analyzed=len(documents),
            valid_documents=[],
            expiring_soon_documents=[],
            expired_documents=[],
            missing_documents=[],
            recommendations=[],
            agent_reasoning=result.get("error", "Unknown error"),
            vessel_info=vessel_info,
            route_ports=request.port_codes
        )

    # Parse the result
    parsed = result.get("parsed_result") or {}

    # Extract data from parsed result or provide defaults
    valid_docs = []
    expiring_docs = []
    expired_docs = []
    missing_docs = []
    recommendations = []
    compliance_score = parsed.get("compliance_score", 0)
    overall_status = parsed.get("overall_status", "PENDING_REVIEW")

    # Process valid documents
    for doc in parsed.get("valid_documents", []):
        valid_docs.append(DocumentSummary(
            document_type=doc.get("document_type", "unknown"),
            expiry_date=doc.get("expiry_date"),
            status="valid",
            days_until_expiry=doc.get("days_until_expiry")
        ))

    # Process expiring soon documents
    for doc in parsed.get("expiring_soon", parsed.get("expiring_soon_documents", [])):
        expiring_docs.append(DocumentSummary(
            document_type=doc.get("document_type", "unknown"),
            expiry_date=doc.get("expiry_date"),
            status="expiring_soon",
            days_until_expiry=doc.get("days_until_expiry")
        ))

    # Process expired documents
    for doc in parsed.get("expired_documents", []):
        expired_docs.append(DocumentSummary(
            document_type=doc.get("document_type", "unknown"),
            expiry_date=doc.get("expiry_date"),
            status="expired",
            days_until_expiry=doc.get("days_until_expiry")
        ))

    # Process missing documents
    for doc in parsed.get("missing_documents", []):
        missing_docs.append(MissingDocument(
            document_type=doc.get("document_type", "unknown"),
            required_by=doc.get("required_by", doc.get("ports_affected", ["Unknown"])),
            priority=doc.get("priority", "HIGH")
        ))

    # Process recommendations
    for rec in parsed.get("recommendations", []):
        recommendations.append(Recommendation(
            priority=rec.get("priority", "MEDIUM"),
            action=rec.get("action", ""),
            documents=rec.get("documents", []),
            deadline=rec.get("deadline")
        ))

    return DocumentAnalysisResponse(
        success=True,
        overall_status=overall_status,
        compliance_score=int(compliance_score),
        documents_analyzed=len(documents),
        valid_documents=valid_docs,
        expiring_soon_documents=expiring_docs,
        expired_documents=expired_docs,
        missing_documents=missing_docs,
        recommendations=recommendations,
        agent_reasoning=result.get("crew_output"),
        vessel_info=vessel_info,
        route_ports=request.port_codes
    )


# ========== Compliance Checking Endpoints ==========

@router.post("/compliance/check-route", response_model=RouteComplianceResponse)
async def check_route_compliance(
    request: RouteComplianceRequest,
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """
    Check route compliance against maritime regulations.
    Returns both structured JSON and natural language report.
    Optionally uses CrewAI agents for comprehensive analysis.
    """
    # Validate vessel exists
    vessel = db.query(Vessel).filter(Vessel.id == request.vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")

    compliance_service = ComplianceService(db)

    if request.use_crewai:
        # Use CrewAI for comprehensive analysis
        orchestrator = get_compliance_orchestrator()

        if not orchestrator.is_available:
            raise HTTPException(
                status_code=503,
                detail="CrewAI not available. Set use_crewai=false for basic compliance check."
            )

        # Prepare vessel info and documents
        vessel_info = {
            "name": vessel.name,
            "imo_number": vessel.imo_number,
            "vessel_type": vessel.vessel_type.value if vessel.vessel_type else "container",
            "flag_state": vessel.flag_state,
            "gross_tonnage": vessel.gross_tonnage,
        }

        doc_service = DocumentService(db)
        user_docs = doc_service.get_vessel_documents(request.vessel_id)
        user_docs_list = [
            {
                "document_type": d.document_type.value,
                "expiry_date": d.expiry_date.isoformat() if d.expiry_date else None,
                "is_expired": d.expiry_date < datetime.now() if d.expiry_date else False,
            }
            for d in user_docs
        ]

        # Run CrewAI compliance check
        crew_result = await orchestrator.check_compliance(
            vessel_info=vessel_info,
            route_ports=request.port_codes,
            user_documents=user_docs_list
        )

        if crew_result.get("error"):
            logger.error(f"CrewAI error: {crew_result['error']}")
            # Fall back to basic compliance check
            result = compliance_service.check_route_compliance(
                vessel_id=request.vessel_id,
                port_codes=request.port_codes,
                route_name=request.route_name
            )
        else:
            # Parse CrewAI result and combine with basic check
            result = compliance_service.check_route_compliance(
                vessel_id=request.vessel_id,
                port_codes=request.port_codes,
                route_name=request.route_name
            )
            # Append CrewAI insights to report
            if crew_result.get("crew_output"):
                result.detailed_report += f"\n\n=== CrewAI Analysis ===\n{crew_result['crew_output']}"

    else:
        # Basic compliance check
        result = compliance_service.check_route_compliance(
            vessel_id=request.vessel_id,
            port_codes=request.port_codes,
            route_name=request.route_name
        )

    # Save to database
    saved_check = compliance_service.save_compliance_check(
        customer_id=customer_id,
        result=result
    )

    return RouteComplianceResponse(
        check_id=saved_check.id,
        vessel_id=result.vessel_id,
        route_name=result.route_name,
        route_ports=result.route_ports,
        overall_status=result.overall_status.value,
        compliance_score=result.compliance_score,
        port_results=[
            PortComplianceResponse(
                port_code=p.port_code,
                port_name=p.port_name,
                status=p.status.value,
                required_documents=p.required_documents,
                missing_documents=p.missing_documents,
                expired_documents=p.expired_documents,
                special_requirements=p.special_requirements,
                risk_factors=p.risk_factors,
            )
            for p in result.port_results
        ],
        missing_documents=result.all_missing_documents,
        recommendations=result.recommendations,
        risk_level=result.risk_level,
        summary_report=result.summary_report,
        detailed_report=result.detailed_report,
    )


@router.post("/compliance/check-port")
async def check_port_compliance(
    vessel_id: int = Query(...),
    port_code: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """Quick compliance check for a single port"""
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")

    compliance_service = ComplianceService(db)
    result = compliance_service.check_port_compliance(vessel_id, port_code)

    return result.to_dict()


@router.get("/compliance/history/{vessel_id}")
async def get_compliance_history(
    vessel_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get compliance check history for a vessel"""
    compliance_service = ComplianceService(db)
    checks = compliance_service.get_compliance_history(vessel_id, limit)

    return [
        {
            "id": c.id,
            "route_name": c.route_name,
            "route_ports": json.loads(c.route_ports) if c.route_ports else [],
            "overall_status": c.overall_status.value if c.overall_status else None,
            "compliance_score": c.compliance_score,
            "created_at": c.created_at.isoformat(),
        }
        for c in checks
    ]


# ========== Knowledge Base Endpoints ==========

@router.post("/kb/search", response_model=KBSearchResponse)
async def search_knowledge_base(request: KBSearchRequest):
    """
    Search maritime regulations knowledge base.

    Filters can include:
    - port: UN/LOCODE
    - region: Asia, Europe, Americas, etc.
    - regulation_type: imo_convention, port_state_control, etc.
    - vessel_type: container, tanker, etc.
    """
    kb = get_maritime_knowledge_base()

    results = kb.search_general(
        query=request.query,
        filters=request.filters,
        top_k=request.top_k,
        collections=request.collections
    )

    return KBSearchResponse(
        results=[
            {
                "content": r.content,
                "metadata": r.metadata,
                "score": r.score,
                "source": r.source,
            }
            for r in results
        ],
        query=request.query,
        total_found=len(results),
    )


@router.get("/kb/port/{port_code}/requirements")
async def get_port_requirements(
    port_code: str,
    vessel_type: Optional[str] = None
):
    """Get all requirements for a specific port"""
    kb = get_maritime_knowledge_base()

    required_docs = kb.search_required_documents(
        port_code=port_code,
        vessel_type=vessel_type or "container"
    )

    port_regulations = kb.search_by_port(
        port_code=port_code,
        vessel_type=vessel_type,
        top_k=10
    )

    return {
        "port_code": port_code,
        "required_documents": required_docs,
        "regulations": [
            {
                "content": r.content,
                "source": r.source,
                "metadata": r.metadata,
            }
            for r in port_regulations
        ],
    }


@router.get("/kb/document-types")
async def list_document_types():
    """List all document types with descriptions"""
    descriptions = {
        DocumentType.SAFETY_CERTIFICATE: "SOLAS Safety Certificates (Passenger/Cargo Ship Safety)",
        DocumentType.LOAD_LINE_CERTIFICATE: "International Load Line Certificate",
        DocumentType.MARPOL_CERTIFICATE: "MARPOL compliance certificates (IOPP, ISPP, etc.)",
        DocumentType.CREW_CERTIFICATE: "STCW certificates of competency for crew",
        DocumentType.ISM_CERTIFICATE: "ISM Code Safety Management Certificate (SMC)",
        DocumentType.ISPS_CERTIFICATE: "ISPS Code International Ship Security Certificate",
        DocumentType.CLASS_CERTIFICATE: "Classification society certificate",
        DocumentType.INSURANCE_CERTIFICATE: "P&I and Hull insurance certificates",
        DocumentType.CUSTOMS_DECLARATION: "Customs declaration documents",
        DocumentType.HEALTH_CERTIFICATE: "Maritime health certificate",
        DocumentType.TONNAGE_CERTIFICATE: "International Tonnage Certificate",
        DocumentType.REGISTRY_CERTIFICATE: "Certificate of Registry",
        DocumentType.CREW_LIST: "Crew list document",
        DocumentType.CARGO_MANIFEST: "Cargo manifest",
        DocumentType.BALLAST_WATER_CERTIFICATE: "BWM Convention certificate",
        DocumentType.OTHER: "Other document types",
    }

    return {
        "document_types": [
            {
                "code": dt.value,
                "name": dt.name.replace("_", " ").title(),
                "description": descriptions.get(dt, ""),
            }
            for dt in DocumentType
        ]
    }


@router.get("/kb/stats")
async def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    kb = get_maritime_knowledge_base()
    stats = kb.get_collection_stats()

    return {
        "collections": stats,
        "total_documents": sum(stats.values()),
        "embeddings_configured": kb.embeddings is not None,
    }


# ========== Port Data Endpoints ==========

@router.get("/ports")
async def list_ports(
    region: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all ports with optional region filter"""
    query = db.query(Port)

    if region:
        query = query.filter(Port.region == region)

    ports = query.limit(limit).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "un_locode": p.un_locode,
            "country": p.country,
            "region": p.region,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "psc_regime": p.psc_regime.value if p.psc_regime else None,
            "is_eca": p.is_eca,
        }
        for p in ports
    ]


@router.get("/ports/{port_code}")
async def get_port(port_code: str, db: Session = Depends(get_db)):
    """Get port details"""
    port = db.query(Port).filter(Port.un_locode == port_code).first()

    if not port:
        raise HTTPException(status_code=404, detail="Port not found")

    return {
        "id": port.id,
        "name": port.name,
        "un_locode": port.un_locode,
        "country": port.country,
        "country_code": port.country_code,
        "region": port.region,
        "latitude": port.latitude,
        "longitude": port.longitude,
        "psc_regime": port.psc_regime.value if port.psc_regime else None,
        "is_eca": port.is_eca,
        "has_shore_power": port.has_shore_power,
        "max_draft": port.max_draft,
    }


# ========== Structured Business Reports Endpoints ==========

class BusinessQueryRequest(BaseModel):
    """Request model for business-friendly knowledge base queries"""
    query: str = Field(..., min_length=3, description="Natural language query")
    vessel_type: Optional[str] = Field(None, description="Vessel type for context")
    port_codes: Optional[List[str]] = Field(None, description="Relevant port codes")
    top_k: int = Field(default=10, ge=1, le=20)


class StructuredReportRequest(BaseModel):
    """Request model for full structured compliance report"""
    vessel_id: int
    port_codes: List[str] = Field(..., min_length=1)
    voyage_start_date: Optional[str] = Field(None, description="ISO date format: YYYY-MM-DD")
    include_documents: bool = Field(default=True, description="Include user document analysis")


@router.post("/reports/query", summary="Query regulations with business-friendly response")
async def query_regulations_for_business(request: BusinessQueryRequest):
    """
    Query maritime regulations and get a structured, business-friendly response.
    
    Returns:
    - Relevant regulations categorized by priority
    - Required documents identified
    - Prioritized action items
    - Risk factors
    - Source references
    
    This endpoint is designed for business users who need actionable compliance information.
    """
    kb = get_maritime_knowledge_base()
    
    result = kb.query_for_business(
        query=request.query,
        vessel_type=request.vessel_type,
        port_codes=request.port_codes,
        top_k=request.top_k
    )
    
    return result


@router.get("/reports/port/{port_code}", summary="Get structured port requirements")
async def get_structured_port_report(
    port_code: str,
    vessel_type: str = Query(default="cargo_ship", description="Vessel type")
):
    """
    Get comprehensive, structured port requirements for business users.
    
    Returns requirements organized by category:
    - Pre-arrival requirements
    - Documentation requirements
    - Environmental requirements
    - Safety requirements
    - Customs requirements
    
    Also includes a compliance checklist with phased actions.
    """
    kb = get_maritime_knowledge_base()
    
    result = kb.get_structured_port_requirements(
        port_code=port_code,
        vessel_type=vessel_type
    )
    
    return result


@router.post("/reports/route-summary", summary="Get structured route compliance summary")
async def get_route_compliance_summary(
    port_codes: List[str] = Query(..., description="Port codes in route order"),
    vessel_type: str = Query(default="cargo_ship"),
    gross_tonnage: Optional[float] = Query(None),
    flag_state: Optional[str] = Query(None)
):
    """
    Generate a business-friendly compliance summary for an entire route.
    
    Returns:
    - Executive summary with key metrics
    - Port-by-port requirement summaries
    - Common documents needed across all ports
    - Prioritized action items
    - Risk assessment
    - Recommendations
    
    Ideal for voyage planning and compliance review meetings.
    """
    kb = get_maritime_knowledge_base()
    
    vessel_info = {
        "vessel_type": vessel_type,
        "gross_tonnage": gross_tonnage,
        "flag_state": flag_state,
    }
    
    result = kb.get_compliance_summary_for_route(
        port_codes=port_codes,
        vessel_info=vessel_info
    )
    
    return result


@router.post("/reports/compliance-report", response_model=ComplianceReport, summary="Generate full compliance report")
async def generate_full_compliance_report(
    request: StructuredReportRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a comprehensive structured compliance report for a vessel and route.
    
    This is the most complete report format, including:
    - Executive summary with compliance score and risk level
    - Document gap analysis (if documents are uploaded)
    - Port-by-port requirements
    - IMO convention requirements
    - Regional requirements (EU MRV, ECA, etc.)
    - Risk assessments with probability and impact
    - Prioritized action items with deadlines
    - Compliance timeline
    
    The report follows the ComplianceReport model structure, making it
    suitable for programmatic processing or display in business dashboards.
    """
    # Validate vessel exists
    vessel = db.query(Vessel).filter(Vessel.id == request.vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")
    
    # Parse voyage start date
    voyage_start = None
    if request.voyage_start_date:
        try:
            from datetime import date
            voyage_start = date.fromisoformat(request.voyage_start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Prepare vessel info
    vessel_info = {
        "vessel_name": vessel.name,
        "imo_number": vessel.imo_number,
        "vessel_type": vessel.vessel_type.value if vessel.vessel_type else "cargo_ship",
        "flag_state": vessel.flag_state,
        "gross_tonnage": vessel.gross_tonnage,
        "year_built": vessel.year_built,
        "classification_society": vessel.classification_society,
    }
    
    # Get user documents if requested
    user_documents = []
    if request.include_documents:
        doc_service = DocumentService(db)
        docs = doc_service.get_vessel_documents(request.vessel_id)
        user_documents = [
            {
                "document_type": d.document_type.value if d.document_type else "other",
                "expiry_date": d.expiry_date.date() if d.expiry_date else None,
            }
            for d in docs
        ]
    
    # Generate the report
    report_generator = get_compliance_report_generator()
    
    report = report_generator.generate_compliance_report(
        vessel_info=vessel_info,
        route_ports=request.port_codes,
        user_documents=user_documents,
        voyage_start_date=voyage_start
    )
    
    return report


@router.get("/reports/quick-check", response_model=QuickComplianceCheck, summary="Quick compliance check for a query")
async def quick_compliance_check(
    query: str = Query(..., min_length=3, description="Compliance question"),
    vessel_type: Optional[str] = Query(None),
    port_code: Optional[str] = Query(None)
):
    """
    Perform a quick compliance check based on a natural language query.
    
    Examples:
    - "What certificates do I need for a container ship going to Rotterdam?"
    - "Do I need a scrubber for Baltic Sea ECA?"
    - "What are the pre-arrival requirements for Singapore?"
    
    Returns a quick assessment with:
    - Status (COMPLIANT, PARTIAL, NON_COMPLIANT, PENDING_REVIEW)
    - Key findings
    - Required documents
    - Action items
    - Risk level
    """
    kb = get_maritime_knowledge_base()
    
    # Search knowledge base
    business_result = kb.query_for_business(
        query=query,
        vessel_type=vessel_type,
        port_codes=[port_code] if port_code else None,
        top_k=5
    )
    
    # Analyze results to determine compliance status
    findings = []
    required_docs = business_result.get("documents_needed", [])
    action_items = []
    
    # Extract findings from regulations
    for reg in business_result.get("regulations", []):
        findings.append(f"{reg['regulation']}: {reg['title']}")
    
    # Convert action items to proper format
    for action in business_result.get("action_items", []):
        action_items.append(ActionItem(
            action_id=f"QC-{len(action_items)+1:03d}",
            priority=Priority(action.get("priority", "MEDIUM")),
            category=action.get("category", "General"),
            action=action.get("action", ""),
            reason=action.get("reason", ""),
            regulation_reference="See sources",
        ))
    
    # Determine overall status and risk level
    risk_factors = business_result.get("risk_factors", [])
    
    if risk_factors:
        status = ComplianceStatus.PENDING_REVIEW
        risk_level = RiskLevel.HIGH
    elif required_docs:
        status = ComplianceStatus.PARTIAL
        risk_level = RiskLevel.MEDIUM
    else:
        status = ComplianceStatus.PENDING_REVIEW
        risk_level = RiskLevel.LOW
    
    # Calculate confidence based on results
    total_results = business_result.get("metadata", {}).get("total_results", 0)
    confidence = min(0.9, total_results * 0.1) if total_results > 0 else 0.3
    
    return QuickComplianceCheck(
        query=query,
        status=status,
        findings=findings[:5],
        required_documents=required_docs[:10],
        action_items=action_items,
        risk_level=risk_level,
        confidence=confidence,
        sources=business_result.get("sources", [])
    )


# ========== Health Check ==========

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    kb = get_maritime_knowledge_base()
    compliance_orchestrator = get_compliance_orchestrator()
    document_orchestrator = get_document_analysis_orchestrator()

    return {
        "status": "healthy",
        "knowledge_base": {
            "collections": list(kb.COLLECTIONS.keys()),
            "embeddings_configured": kb.embeddings is not None,
        },
        "crewai_compliance_available": compliance_orchestrator.is_available,
        "crewai_document_analysis_available": document_orchestrator.is_available,
        "timestamp": datetime.now().isoformat(),
    }
