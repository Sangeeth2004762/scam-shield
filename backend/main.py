"""
Scam Shield - FastAPI Application Server
Provides REST API endpoints for text/screenshot scam analysis, cybercrime report drafting,
history storage, and threat statistics.
"""

from __future__ import annotations
import os
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, Request, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, select
from dotenv import load_dotenv

try:
    from .models import (
        AnalyzeTextRequest,
        AnalyzeResponse,
        ExtractedEntities,
        RuleFindingItem,
        AnalysisRecord,
        HistoryResponse,
        HistoryItem,
        StatsResponse,
        CategoryStat,
        VerdictStat,
        ReportDraft,
        LanguageType
    )
    from .rules import RuleEngine
    from .database import init_db, get_session
    from .report_helper import build_report_draft
    from .llm import LLMAnalyzer, calculate_final_scores
except (ImportError, ValueError):
    from models import (
        AnalyzeTextRequest,
        AnalyzeResponse,
        ExtractedEntities,
        RuleFindingItem,
        AnalysisRecord,
        HistoryResponse,
        HistoryItem,
        StatsResponse,
        CategoryStat,
        VerdictStat,
        ReportDraft,
        LanguageType
    )
    from rules import RuleEngine
    from database import init_db, get_session
    from report_helper import build_report_draft
    from llm import LLMAnalyzer, calculate_final_scores

load_dotenv()
logger = logging.getLogger("scam_shield.api")

# Rate limiter setup (key by client IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

rule_engine = RuleEngine()
llm_analyzer = LLMAnalyzer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    init_db()
    yield


app = FastAPI(
    title="Scam Shield API",
    description="AI-Powered Scam Detector & Cybersecurity Assistant for Indian Users",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify backend status and AI provider availability."""
    provider = llm_analyzer.provider
    return {
        "status": "healthy",
        "service": "Scam Shield API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "ai_provider": {
            "name": type(provider).__name__,
            "is_available": provider.is_available(),
            "model": getattr(provider, "model_name", "unknown")
        }
    }


def synthesize_rule_only_response(
    text: str,
    sender: Optional[str],
    language: LanguageType,
    rule_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synthesizes plain-language explanation and action steps directly from the rule engine findings.
    Used when Gemini API key is absent or as immediate fallback.
    """
    verdict = rule_result["preliminary_verdict"]
    top_cat = rule_result["top_category"]
    score = rule_result["rule_score"]
    findings = rule_result["findings"]

    # Red flag strings
    red_flag_texts = [f["description"] for f in findings]
    if not red_flag_texts:
        if verdict == "LIKELY_SAFE":
            red_flag_texts = ["No overt phishing indicators or extortion patterns detected."]
        else:
            red_flag_texts = ["Message contains unsolicited commercial or unusual patterns."]

    # Explanations in requested language
    if language == "ta":
        if verdict == "SCAM":
            explanation = "இந்த செய்தி மோசடி நோக்கத்துடன் அனுப்பப்பட்டதாக தெரிகிறது. அவசரப்படுத்தி உங்களை தவறாக வழிநடத்த முயற்சிக்கின்றனர். இதில் உள்ள இணைப்புகளையோ அல்லது கோரிக்கைகளையோ நம்ப வேண்டாம்."
            what_to_do = [
                "எந்தவொரு இணைப்பையும் (Links) கிளிக் செய்யாதீர்கள் மற்றும் ஆப்-களை (APK) நிறுவ வேண்டாம்.",
                "உங்கள் OTP, UPI பின் (PIN), அல்லது வங்கி விவரங்களை யாரிடமும் பகிராதீர்கள்.",
                "சந்தேகத்திற்கிடமான எண்களை உடனே பிளாக் செய்து சைபர் கிரைம் உதவி எண் 1930-ல் புகாரளிக்கவும்."
            ]
        elif verdict == "SUSPICIOUS":
            explanation = "இந்த செய்தியில் சில சந்தேகத்திற்கிடமான அம்சங்கள் உள்ளன. இது உண்மையான நிறுவனத்திடமிருந்து வந்ததா என்பதை உறுதிப்படுத்தவும்."
            what_to_do = [
                "உடனே பணம் அனுப்பவோ அல்லது விவரங்களை உள்ளிடவோ வேண்டாம்.",
                "அதிகாரப்பூர்வ வாடிக்கையாளர் சேவை எண்ணை நேரடியாக தொடர்பு கொள்ளவும்.",
                "வங்கி ஆப் மூலம் மட்டுமே உங்கள் கணக்கு நிலவரத்தை சரிபார்க்கவும்."
            ]
        else:
            explanation = "இந்த செய்தி பொதுவாக பாதுகாப்பானதாக தெரிகிறது. இதில் பொதுவான மோசடி வாசகங்களோ அபாயகரமான இணைப்புகளோ கண்டறியப்படவில்லை."
            what_to_do = [
                "பாதுகாப்பான பரிவர்த்தனைகளுக்கு எப்போதும் அதிகாரப்பூர்வ செயலிகளை மட்டும் பயன்படுத்தவும்.",
                "உங்கள் ரகசிய பின் அல்லது OTP-ஐ யாருடனும் ஒருபோதும் பகிர வேண்டாம்."
            ]
    elif language == "hi":
        if verdict == "SCAM":
            explanation = "यह संदेश स्पष्ट रूप से धोखाधड़ी और साइबर स्कैम प्रतीत होता है। इसमें आपको डराकर या लालच देकर व्यक्तिगत जानकारी या पैसे ऐंठने की कोशिश की गई है।"
            what_to_do = [
                "संदेश में दिए गए किसी भी लिंक पर क्लिक न करें और कोई APK फाइल इंस्टॉल न करें।",
                "अपना ओटीपी (OTP), यूपीआई पिन (UPI PIN) या पासवर्ड किसी के साथ साझा न करें।",
                "यदि पैसे कट गए हैं तो तुरंत 1930 पर कॉल करें और cybercrime.gov.in पर रिपोर्ट करें।"
            ]
        elif verdict == "SUSPICIOUS":
            explanation = "इस संदेश में कुछ संदिग्ध पैटर्न पाए गए हैं। बिना जांचे-परखे किसी भी दावे पर विश्वास न करें।"
            what_to_do = [
                "जल्दबाजी में कोई कदम न उठाएं और किसी अज्ञात खाते में पैसे न भेजें।",
                "संबंधित बैंक या संस्थान की आधिकारिक वेबसाइट पर जाकर स्थिति की पुष्टि करें।",
                "संदिग्ध नंबर को तुरंत ब्लॉक करें।"
            ]
        else:
            explanation = "यह संदेश सुरक्षित प्रतीत होता है। इसमें कोई ज्ञात धोखाधड़ी या फ़िशिंग लिंक नहीं पाया गया है।"
            what_to_do = [
                "लेनदेन के लिए हमेशा केवल आधिकारिक बैंक या ई-कॉमर्स ऐप का ही उपयोग करें।",
                "याद रखें कि कोई भी बैंक आपसे कभी भी आपका पिन या ओटीपी नहीं मांगता।"
            ]
    else:  # English default
        if verdict == "SCAM":
            explanation = "This message strongly matches active cyber scam patterns targeting Indian citizens. It employs artificial urgency, brand impersonation, or threats to manipulate you into losing money or credentials."
            what_to_do = [
                "Do NOT click any links, open attachments, or download any APK files.",
                "NEVER enter your UPI PIN to 'receive' money or refunds—PIN is only for paying out.",
                "Block the sender and report the incident via national cyber helpline 1930 or cybercrime.gov.in."
            ]
        elif verdict == "SUSPICIOUS":
            explanation = "This message displays suspicious characteristics, such as unverified sender origins or vague claims. Proceed with extreme caution."
            what_to_do = [
                "Verify the claim by logging into the provider's official mobile application independently.",
                "Do not call any phone numbers listed inside the message text.",
                "Never share OTPs or personal identity documents over unverified channels."
            ]
        else:
            explanation = "This message appears legitimate and safe. It exhibits typical characteristics of standard transactional alerts without deceptive links or intimidation."
            what_to_do = [
                "Always check that transaction amounts match your recent activity.",
                "Remember that banks and genuine delivery agents never ask for confidential PINs or OTPs."
            ]

    return {
        "verdict": verdict,
        "risk_score": score,
        "rule_score": score,
        "llm_score": score,
        "scam_category": top_cat,
        "red_flags": red_flag_texts,
        "explanation": explanation,
        "what_to_do": what_to_do,
        "confidence": 0.88 if verdict != "SUSPICIOUS" else 0.70,
        "model_used": "deterministic_rule_engine"
    }


@app.post("/api/analyze/text", response_model=AnalyzeResponse, tags=["Scam Analysis"])
@limiter.limit("30/minute")
async def analyze_text(
    request: Request,
    payload: AnalyzeTextRequest,
    session: Session = Depends(get_session)
) -> AnalyzeResponse:
    """
    Analyzes pasted message text for scam patterns, combines rule engine findings
    with Gemini AI reasoning, generates cybercrime complaint drafts, and optionally records history.
    """
    try:
        # Step 1: Run deterministic rule engine
        rule_eval = rule_engine.evaluate(payload.text, sender=payload.sender)

        # Step 2: Run LLM analysis (with retry and graceful fallback to rule engine)
        analysis_data = llm_analyzer.analyze(
            text=payload.text,
            sender=payload.sender,
            language=payload.language,
            rule_result=rule_eval,
            fallback_func=synthesize_rule_only_response
        )

        entities = ExtractedEntities(**rule_eval["entities"])
        rule_findings = [
            RuleFindingItem(
                rule_id=f["rule_id"],
                description=f["description"],
                weight=f["weight"],
                category=f.get("category", "OTHER")
            )
            for f in rule_eval["findings"]
        ]

        # Step 3: Build cybercrime report draft for SCAM / SUSPICIOUS
        report_draft: Optional[ReportDraft] = None
        if analysis_data["verdict"] in ("SCAM", "SUSPICIOUS"):
            report_draft = build_report_draft(
                message_text=payload.text,
                scam_category=analysis_data["scam_category"],
                sender=payload.sender,
                entities=entities,
                red_flags=analysis_data["red_flags"]
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        record_id = None

        # Step 4: Persist in SQLite history if user opted in
        if payload.save_history:
            record = AnalysisRecord(
                input_type="text",
                message_snippet=payload.text[:200],
                full_text=payload.text[:1000],
                sender=payload.sender,
                language=payload.language,
                verdict=analysis_data["verdict"],
                risk_score=analysis_data["risk_score"],
                rule_score=analysis_data["rule_score"],
                llm_score=analysis_data["llm_score"],
                scam_category=analysis_data["scam_category"],
                red_flags_json=json.dumps(analysis_data["red_flags"]),
                explanation=analysis_data["explanation"],
                what_to_do_json=json.dumps(analysis_data["what_to_do"]),
                confidence=analysis_data["confidence"],
                model_used=analysis_data["model_used"]
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            record_id = record.id

        return AnalyzeResponse(
            id=record_id,
            verdict=analysis_data["verdict"],
            risk_score=analysis_data["risk_score"],
            rule_score=analysis_data["rule_score"],
            llm_score=analysis_data["llm_score"],
            scam_category=analysis_data["scam_category"],
            red_flags=analysis_data["red_flags"],
            explanation=analysis_data["explanation"],
            what_to_do=analysis_data["what_to_do"],
            confidence=analysis_data["confidence"],
            entities=entities,
            rule_findings=rule_findings,
            language=payload.language,
            report_draft=report_draft,
            model_used=analysis_data["model_used"],
            analyzed_at=now_iso
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing text: {str(e)}"
        )


@app.post("/api/analyze/image", response_model=AnalyzeResponse, tags=["Scam Analysis"])
@limiter.limit("15/minute")
async def analyze_image(
    request: Request,
    file: UploadFile = File(..., description="Screenshot of SMS, WhatsApp, or email (PNG/JPG)"),
    sender: Optional[str] = Form(None),
    language: LanguageType = Form("en"),
    save_history: bool = Form(True),
    session: Session = Depends(get_session)
) -> AnalyzeResponse:
    """
    Uploads a screenshot, transcribes the message text with Gemini Vision, runs the rule engine,
    and produces a comprehensive scam verdict and cybercrime report draft.
    """
    # Validate content type
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    content_type = file.content_type or ""
    if content_type.lower() not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: '{content_type}'. Please upload PNG, JPG, or WEBP."
        )

    # Read bytes and validate file size (max 10MB)
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}"
        )

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image size exceeds 10MB limit."
        )

    if not llm_analyzer.provider.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Screenshot vision analysis requires a configured Google Gemini API key. Please set GEMINI_API_KEY or use the text analysis option."
        )

    try:
        extracted_text, analysis_data = llm_analyzer.analyze_image(
            image_bytes=contents,
            mime_type=content_type,
            sender=sender,
            language=language,
            rule_engine_instance=rule_engine,
            fallback_func=synthesize_rule_only_response
        )

        rule_eval = analysis_data["rule_eval"]
        entities = ExtractedEntities(**rule_eval["entities"])
        rule_findings = [
            RuleFindingItem(
                rule_id=f["rule_id"],
                description=f["description"],
                weight=f["weight"],
                category=f.get("category", "OTHER")
            )
            for f in rule_eval["findings"]
        ]

        report_draft: Optional[ReportDraft] = None
        if analysis_data["verdict"] in ("SCAM", "SUSPICIOUS"):
            report_draft = build_report_draft(
                message_text=extracted_text or "[Image Screenshot]",
                scam_category=analysis_data["scam_category"],
                sender=sender,
                entities=entities,
                red_flags=analysis_data["red_flags"]
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        record_id = None

        if save_history:
            record = AnalysisRecord(
                input_type="image",
                message_snippet=extracted_text[:200] if extracted_text else "Screenshot Analysis",
                full_text=extracted_text[:1000] if extracted_text else None,
                sender=sender,
                language=language,
                verdict=analysis_data["verdict"],
                risk_score=analysis_data["risk_score"],
                rule_score=analysis_data["rule_score"],
                llm_score=analysis_data["llm_score"],
                scam_category=analysis_data["scam_category"],
                red_flags_json=json.dumps(analysis_data["red_flags"]),
                explanation=analysis_data["explanation"],
                what_to_do_json=json.dumps(analysis_data["what_to_do"]),
                confidence=analysis_data["confidence"],
                model_used=analysis_data["model_used"]
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            record_id = record.id

        return AnalyzeResponse(
            id=record_id,
            verdict=analysis_data["verdict"],
            risk_score=analysis_data["risk_score"],
            rule_score=analysis_data["rule_score"],
            llm_score=analysis_data["llm_score"],
            scam_category=analysis_data["scam_category"],
            red_flags=analysis_data["red_flags"],
            explanation=analysis_data["explanation"],
            what_to_do=analysis_data["what_to_do"],
            confidence=analysis_data["confidence"],
            entities=entities,
            rule_findings=rule_findings,
            language=language,
            report_draft=report_draft,
            model_used=analysis_data["model_used"],
            analyzed_at=now_iso,
            ocr_extracted_text=extracted_text
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing image: {str(e)}"
        )


@app.get("/api/history", response_model=HistoryResponse, tags=["History & Insights"])
async def get_history(
    limit: int = 50,
    session: Session = Depends(get_session)
) -> HistoryResponse:
    """Retrieves recent scan history."""
    try:
        statement = select(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).limit(limit)
        records = session.exec(statement).all()

        items: List[HistoryItem] = []
        for r in records:
            try:
                flags = json.loads(r.red_flags_json)
            except Exception:
                flags = []
            try:
                actions = json.loads(r.what_to_do_json)
            except Exception:
                actions = []

            items.append(
                HistoryItem(
                    id=r.id,
                    created_at=r.created_at.isoformat(),
                    input_type=r.input_type,
                    message_snippet=r.message_snippet,
                    sender=r.sender,
                    language=r.language,
                    verdict=r.verdict,
                    risk_score=r.risk_score,
                    scam_category=r.scam_category,
                    red_flags=flags,
                    explanation=r.explanation,
                    what_to_do=actions,
                    confidence=r.confidence
                )
            )

        return HistoryResponse(total=len(items), items=items)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching history: {str(e)}"
        )


@app.get("/api/stats", response_model=StatsResponse, tags=["History & Insights"])
async def get_stats(
    session: Session = Depends(get_session)
) -> StatsResponse:
    """Calculates aggregated metrics, category breakdowns, and verdict distributions."""
    try:
        records = session.exec(select(AnalysisRecord)).all()
        total = len(records)

        if total == 0:
            return StatsResponse(
                total_scans=0,
                verdict_distribution=[],
                category_distribution=[],
                avg_risk_score=0.0,
                high_risk_scam_count=0
            )

        verdict_counts: Dict[str, int] = {}
        category_counts: Dict[str, int] = {}
        total_risk = 0
        high_risk = 0

        for r in records:
            verdict_counts[r.verdict] = verdict_counts.get(r.verdict, 0) + 1
            if r.scam_category != "NONE":
                category_counts[r.scam_category] = category_counts.get(r.scam_category, 0) + 1
            total_risk += r.risk_score
            if r.risk_score >= 70:
                high_risk += 1

        v_stats = [
            VerdictStat(
                verdict=v,
                count=c,
                percentage=round((c / total) * 100, 1)
            )
            for v, c in verdict_counts.items()
        ]

        c_total = sum(category_counts.values()) or 1
        c_stats = [
            CategoryStat(
                category=cat,
                count=c,
                percentage=round((c / c_total) * 100, 1)
            )
            for cat, c in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return StatsResponse(
            total_scans=total,
            verdict_distribution=v_stats,
            category_distribution=c_stats,
            avg_risk_score=round(total_risk / total, 1),
            high_risk_scam_count=high_risk
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error computing stats: {str(e)}"
        )
