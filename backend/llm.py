"""
Scam Shield - LLM Analysis Engine
Integrates Gemini API with deterministic rule findings, enforces strict JSON validation,
handles retry on schema mismatch, and falls back to rule-based analysis if LLM is unavailable.
"""

from __future__ import annotations
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from pydantic import ValidationError

try:
    from .models import LLMAnalysisOutput, LanguageType, ScamCategoryType, VerdictType
    from .provider import get_llm_provider, BaseLLMProvider
except (ImportError, ValueError):
    from models import LLMAnalysisOutput, LanguageType, ScamCategoryType, VerdictType
    from provider import get_llm_provider, BaseLLMProvider

logger = logging.getLogger("scam_shield.llm")

# System prompt specialized for Indian cyber threats
SYSTEM_PROMPT = """You are 'Scam Shield', an expert AI cybersecurity analyst and fraud investigator specialized in the Indian cyber threat landscape.
Your mission is to evaluate communications (SMS, WhatsApp messages, emails, social media messages, phone transcripts) and protect Indian citizens from fraud.

You have comprehensive knowledge of active Indian cyber scams:
1. Bank KYC / PAN / Aadhaar Suspension: Fake SMS claiming SBI YONO, HDFC, ICICI, etc. accounts are blocked. RBI rules strictly prohibit banks from asking for KYC updates via SMS links or personal mobile numbers.
2. "Digital Arrest" Extortion: Impersonation of CBI, Crime Branch, ED, Narcotics Control Bureau (NCB), or High Court claiming the victim's Aadhaar or SIM was used to send illegal drug parcels (FedEx/customs). They force victims into continuous Skype/video calls. Law enforcement NEVER conducts trials or digital arrests over video calls.
3. Electricity Bill Disconnection: Fake messages claiming electricity power supply will be cut off at 9:30 PM due to unpaid bills, prompting calls to fake "officers".
4. Work-from-Home / Telegram Prepaid Task: Promises of Rs. 3000-5000/day for liking YouTube videos or writing Google reviews, leading to Ponzi-style deposits on fraudulent websites.
5. Courier / Customs Seizure: Fake FedEx/DHL/India Post notices demanding clearance fees for parcels containing illegal goods.
6. Lottery / KBC Jackpot: Unsolicited claims of winning Rs. 25 Lakh in KBC or car raffles.
7. Predatory Loan Apps: Instant loans offering zero CIBIL check, distributing malicious APKs that steal contacts and extort victims.
8. UPI Collect Request Fraud: Tricks telling victims to 'enter UPI PIN' or accept collect requests to 'receive cashback/refund'. CRITICAL RULE: Entering UPI PIN ALWAYS deducts money; it NEVER credits money.
9. Genuine Messages: Transactional alerts from TRAI-registered headers (e.g. AX-HDFCBK, VK-SBIINB) with OTPs where the message explicitly says 'Do not share OTP', or legitimate e-commerce delivery updates.

RULES FOR YOUR OUTPUT:
- You must output strictly valid JSON matching this schema:
  {
    "verdict": "SCAM" | "SUSPICIOUS" | "LIKELY_SAFE",
    "risk_score": integer from 0 to 100,
    "scam_category": "KYC_BANK" | "PARCEL_COURIER" | "JOB_TASK" | "LOAN_APP" | "DIGITAL_ARREST" | "UTILITY_BILL" | "LOTTERY_PRIZE" | "UPI_COLLECT" | "INVESTMENT_CRYPTO" | "ROMANCE" | "PHISHING_LINK" | "OTHER" | "NONE",
    "red_flags": ["short bullet 1", "short bullet 2", ...],
    "explanation": "2-4 simple, empowering sentences explaining why this is a scam or safe.",
    "what_to_do": ["ordered action step 1", "ordered action step 2", ...],
    "confidence": float between 0.0 and 1.0
  }

LANGUAGE REQUIREMENT:
- If the requested language is 'ta' (Tamil), write the 'explanation' and each bullet in 'what_to_do' in natural, conversational Tamil (தமிழ்).
- If the requested language is 'hi' (Hindi), write the 'explanation' and each bullet in 'what_to_do' in natural, conversational Hindi (हिन्दी).
- If the requested language is 'en' (English), write them in clear, accessible English.
- Keep 'verdict' and 'scam_category' in English uppercase enum values.
- Do NOT wrap in markdown code blocks. Output raw JSON only.
"""


def format_user_prompt(
    text: str,
    sender: Optional[str],
    language: LanguageType,
    rule_findings: List[Dict[str, Any]],
    rule_score: int,
    entities: Dict[str, List[str]]
) -> str:
    """Builds structured input prompt incorporating deterministic rule findings."""
    lang_name = {"en": "English", "ta": "Tamil (தமிழ்)", "hi": "Hindi (हिन्दी)"}.get(language, "English")

    findings_summary = "\n".join(
        f"- [{f['rule_id']}] {f['description']} (Weight: {f['weight']})"
        for f in rule_findings
    ) if rule_findings else "None detected by rule engine."

    entities_summary = (
        f"URLs: {entities.get('urls', [])}\n"
        f"Phones: {entities.get('phones', [])}\n"
        f"UPI IDs: {entities.get('upi_ids', [])}\n"
        f"Amounts: {entities.get('amounts', [])}"
    )

    return f"""Analyze the following message received by an Indian citizen:

--- MESSAGE CONTENT ---
{text}
--- END MESSAGE ---

Sender / Caller ID: {sender or 'Not provided'}
Target Output Language: {lang_name} ({language})

--- PRELIMINARY RULE ENGINE FINDINGS ---
Rule Score: {rule_score}/100
Triggered Heuristics:
{findings_summary}

Extracted Entities:
{entities_summary}
----------------------------------------

Perform a deep contextual analysis, combining the rule findings with your cybercrime threat intelligence.
Produce the final JSON assessment now.
"""


def clean_json_text(raw_text: str) -> str:
    """Strips markdown code fences and extraneous whitespace from LLM output."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def calculate_final_scores(
    rule_score: int,
    llm_score: int,
    llm_verdict: VerdictType,
    rule_findings: List[Dict[str, Any]]
) -> Tuple[int, VerdictType]:
    """
    Computes final combined score using weighted formula:
    Final Score = round(0.35 * rule_score + 0.65 * llm_score)

    Applies critical security guards for high-risk Indian vectors to eliminate false negatives.
    """
    combined_score = round(0.35 * rule_score + 0.65 * llm_score)
    combined_score = max(0, min(100, combined_score))

    # Critical rule guard: if severe indicators are detected, prevent under-scoring
    critical_rules = {
        "DIGITAL_ARREST_EXTORTION",
        "UPI_COLLECT_REVERSE_SCAM",
        "OTP_CREDENTIAL_HARVEST",
        "URL_APK_DOWNLOAD",
        "UTILITY_ELECTRICITY_DISCONNECTION",
        "KYC_ACCOUNT_SUSPENSION"
    }
    has_critical = any(f.get("rule_id") in critical_rules for f in rule_findings)

    final_verdict: VerdictType
    if combined_score >= 70:
        final_verdict = "SCAM"
    elif combined_score >= 35:
        final_verdict = "SUSPICIOUS"
    else:
        final_verdict = "LIKELY_SAFE"

    # Override: if critical cybercrime rule triggered and LLM underestimated risk
    if has_critical and final_verdict == "LIKELY_SAFE":
        combined_score = max(55, combined_score)
        final_verdict = "SUSPICIOUS"

    # If LLM classified as SCAM with high score, respect it
    if llm_verdict == "SCAM" and final_verdict != "SCAM" and llm_score >= 75:
        final_verdict = "SCAM"
        combined_score = max(70, combined_score)

    return combined_score, final_verdict


class LLMAnalyzer:
    """Orchestrates LLM calls, schema validation, retries, and fallback."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None) -> None:
        self.provider = provider or get_llm_provider()

    def analyze(
        self,
        text: str,
        sender: Optional[str],
        language: LanguageType,
        rule_result: Dict[str, Any],
        fallback_func
    ) -> Dict[str, Any]:
        """
        Runs LLM analysis on message text and rule engine output.
        Retries once on JSON/schema error, and seamlessly falls back if provider is unavailable.
        """
        rule_score = rule_result["rule_score"]
        rule_findings = rule_result["findings"]
        entities = rule_result["entities"]

        # Check if provider is available
        if not self.provider.is_available():
            logger.info("LLM provider unavailable or missing API key; using rule engine fallback.")
            return fallback_func(text, sender, language, rule_result)

        prompt = format_user_prompt(
            text=text,
            sender=sender,
            language=language,
            rule_findings=rule_findings,
            rule_score=rule_score,
            entities=entities
        )

        llm_output: Optional[LLMAnalysisOutput] = None

        # Attempt 1
        try:
            raw_response = self.provider.generate_text(
                prompt=prompt,
                system_instruction=SYSTEM_PROMPT
            )
            cleaned = clean_json_text(raw_response)
            parsed = json.loads(cleaned)
            llm_output = LLMAnalysisOutput(**parsed)
        except Exception as err1:
            logger.warning(f"LLM Attempt 1 parsing failed ({err1}); retrying with corrective prompt...")
            # Attempt 2 (Retry once with corrective feedback)
            try:
                retry_prompt = (
                    f"{prompt}\n\nIMPORTANT: Your previous output failed JSON validation: {str(err1)}. "
                    f"Return ONLY a single valid JSON object following the required schema without markdown tags."
                )
                raw_response2 = self.provider.generate_text(
                    prompt=retry_prompt,
                    system_instruction=SYSTEM_PROMPT
                )
                cleaned2 = clean_json_text(raw_response2)
                parsed2 = json.loads(cleaned2)
                llm_output = LLMAnalysisOutput(**parsed2)
            except Exception as err2:
                logger.error(f"LLM Attempt 2 failed ({err2}); activating fallback.")
                return fallback_func(text, sender, language, rule_result)

        # Successful LLM analysis: compute final fused score
        final_score, final_verdict = calculate_final_scores(
            rule_score=rule_score,
            llm_score=llm_output.risk_score,
            llm_verdict=llm_output.verdict,
            rule_findings=rule_findings
        )

        # Combine red flags: LLM flags + unique rule descriptions
        combined_flags = list(llm_output.red_flags)
        for f in rule_findings:
            desc = f["description"]
            if desc not in combined_flags and len(combined_flags) < 8:
                combined_flags.append(desc)

        return {
            "verdict": final_verdict,
            "risk_score": final_score,
            "rule_score": rule_score,
            "llm_score": llm_output.risk_score,
            "scam_category": llm_output.scam_category if final_verdict != "LIKELY_SAFE" else "NONE",
            "red_flags": combined_flags,
            "explanation": llm_output.explanation,
            "what_to_do": llm_output.what_to_do,
            "confidence": llm_output.confidence,
            "model_used": getattr(self.provider, "model_name", "gemini-flash")
        }

    def analyze_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        sender: Optional[str],
        language: LanguageType,
        rule_engine_instance,
        fallback_func
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Uses Gemini Vision to extract text from a screenshot and evaluate the scam.
        Returns: (extracted_text, analysis_dict)
        """
        if not self.provider.is_available():
            raise RuntimeError("Gemini Vision requires a valid GEMINI_API_KEY to inspect image screenshots.")

        vision_system_instruction = (
            SYSTEM_PROMPT + "\n\nIn addition to the analysis schema, you must include an 'extracted_text' key "
            "containing the verbatim text transcribed from the screenshot."
        )

        lang_name = {"en": "English", "ta": "Tamil (தமிழ்)", "hi": "Hindi (हिन्दी)"}.get(language, "English")
        vision_prompt = f"""This image is a screenshot of an SMS, WhatsApp chat, email, or mobile screen received by an Indian citizen.
1. Transcribe all text visible in the image accurately into an 'extracted_text' field.
2. Analyze the image and text for Indian cyber scam patterns (KYC, digital arrest, electricity bill, job review, fake loan APK, UPI collect, lottery).
3. Target explanation and what_to_do language: {lang_name} ({language}).

Return strictly valid JSON with:
- "extracted_text": verbatim transcription
- "verdict": "SCAM" | "SUSPICIOUS" | "LIKELY_SAFE"
- "risk_score": 0-100
- "scam_category": category enum
- "red_flags": [short strings]
- "explanation": 2-4 sentences
- "what_to_do": [ordered steps]
- "confidence": 0.0-1.0
"""
        raw_response = self.provider.generate_vision(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=vision_prompt,
            system_instruction=vision_system_instruction
        )

        cleaned = clean_json_text(raw_response)
        parsed = json.loads(cleaned)
        extracted_text = parsed.get("extracted_text", "").strip()

        # Run rule engine on the transcribed text to compute rule score
        rule_result = rule_engine_instance.evaluate(extracted_text, sender=sender)
        rule_score = rule_result["rule_score"]
        rule_findings = rule_result["findings"]

        llm_score = int(parsed.get("risk_score", 50))
        llm_verdict = parsed.get("verdict", "SUSPICIOUS")

        final_score, final_verdict = calculate_final_scores(
            rule_score=rule_score,
            llm_score=llm_score,
            llm_verdict=llm_verdict,
            rule_findings=rule_findings
        )

        combined_flags = parsed.get("red_flags", [])
        for f in rule_findings:
            desc = f["description"]
            if desc not in combined_flags and len(combined_flags) < 8:
                combined_flags.append(desc)

        analysis = {
            "verdict": final_verdict,
            "risk_score": final_score,
            "rule_score": rule_score,
            "llm_score": llm_score,
            "scam_category": parsed.get("scam_category", "OTHER") if final_verdict != "LIKELY_SAFE" else "NONE",
            "red_flags": combined_flags,
            "explanation": parsed.get("explanation", "Screenshot analyzed."),
            "what_to_do": parsed.get("what_to_do", []),
            "confidence": float(parsed.get("confidence", 0.85)),
            "model_used": getattr(self.provider, "model_name", "gemini-flash-vision"),
            "rule_eval": rule_result
        }

        return extracted_text, analysis
