"""
Scam Shield - Data Models & Schemas
Contains Pydantic schemas for API request/response validation and SQLModel entity for SQLite persistence.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional, Literal, Dict, Any
from uuid import uuid4
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as DBField


# Allowed scam categories
ScamCategoryType = Literal[
    "KYC_BANK",
    "PARCEL_COURIER",
    "JOB_TASK",
    "LOAN_APP",
    "DIGITAL_ARREST",
    "UTILITY_BILL",
    "LOTTERY_PRIZE",
    "UPI_COLLECT",
    "INVESTMENT_CRYPTO",
    "ROMANCE",
    "PHISHING_LINK",
    "OTHER",
    "NONE"
]

VerdictType = Literal["SCAM", "SUSPICIOUS", "LIKELY_SAFE"]
LanguageType = Literal["en", "ta", "hi"]


# --- API Request Schemas ---

class AnalyzeTextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=3,
        max_length=15000,
        description="Pasted SMS, WhatsApp message, email, or scam text."
    )
    sender: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional sender mobile number, header (e.g. VK-SBIINB), or URL."
    )
    language: LanguageType = Field(
        "en",
        description="Target language for explanation and advice: 'en' (English), 'ta' (Tamil), 'hi' (Hindi)."
    )
    save_history: bool = Field(
        True,
        description="Whether to save this analysis to local history (user can opt out for privacy)."
    )


# --- Rule Engine & Entity Schemas ---

class ExtractedEntities(BaseModel):
    urls: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    upi_ids: List[str] = Field(default_factory=list)
    amounts: List[str] = Field(default_factory=list)


class RuleFindingItem(BaseModel):
    rule_id: str
    description: str
    weight: int
    category: str


# --- Cybercrime Report Draft Schema ---

class ReportDraft(BaseModel):
    incident_date: str
    category: str
    incident_summary: str
    suspect_identifiers: str
    evidence_text: str
    reported_loss_amount: str
    helpline_number: str = "1930"
    portal_url: str = "https://cybercrime.gov.in"
    chakshu_url: str = "https://sancharsaathi.gov.in/sfc/"
    full_complaint_text: str


# --- LLM Internal Output Schema ---

class LLMAnalysisOutput(BaseModel):
    verdict: VerdictType
    risk_score: int = Field(..., ge=0, le=100)
    scam_category: ScamCategoryType
    red_flags: List[str] = Field(default_factory=list)
    explanation: str
    what_to_do: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


# --- Final Unified API Response ---

class AnalyzeResponse(BaseModel):
    id: Optional[str] = None
    verdict: VerdictType
    risk_score: int = Field(..., ge=0, le=100, description="Final weighted risk score (0-100)")
    rule_score: int = Field(..., ge=0, le=100, description="Deterministic rule score (0-100)")
    llm_score: int = Field(..., ge=0, le=100, description="LLM semantic risk score (0-100)")
    scam_category: ScamCategoryType
    red_flags: List[str]
    explanation: str
    what_to_do: List[str]
    confidence: float
    entities: ExtractedEntities
    rule_findings: List[RuleFindingItem]
    language: LanguageType
    report_draft: Optional[ReportDraft] = None
    model_used: str
    analyzed_at: str
    ocr_extracted_text: Optional[str] = None


# --- Database Entity ---

class AnalysisRecord(SQLModel, table=True):
    __tablename__ = "analysis_history"

    id: str = DBField(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime = DBField(default_factory=lambda: datetime.now(timezone.utc))
    input_type: str = DBField(default="text")  # "text" or "image"
    message_snippet: str = DBField(default="")
    full_text: Optional[str] = DBField(default=None)
    sender: Optional[str] = DBField(default=None)
    language: str = DBField(default="en")
    verdict: str = DBField(index=True)
    risk_score: int = DBField(default=0)
    rule_score: int = DBField(default=0)
    llm_score: int = DBField(default=0)
    scam_category: str = DBField(index=True)
    red_flags_json: str = DBField(default="[]")
    explanation: str = DBField(default="")
    what_to_do_json: str = DBField(default="[]")
    confidence: float = DBField(default=0.0)
    model_used: str = DBField(default="rule_fallback")


# --- Stats & History Response Schemas ---

class HistoryItem(BaseModel):
    id: str
    created_at: str
    input_type: str
    message_snippet: str
    sender: Optional[str]
    language: str
    verdict: str
    risk_score: int
    scam_category: str
    red_flags: List[str]
    explanation: str
    what_to_do: List[str]
    confidence: float


class HistoryResponse(BaseModel):
    total: int
    items: List[HistoryItem]


class CategoryStat(BaseModel):
    category: str
    count: int
    percentage: float


class VerdictStat(BaseModel):
    verdict: str
    count: int
    percentage: float


class StatsResponse(BaseModel):
    total_scans: int
    verdict_distribution: List[VerdictStat]
    category_distribution: List[CategoryStat]
    avg_risk_score: float
    high_risk_scam_count: int
