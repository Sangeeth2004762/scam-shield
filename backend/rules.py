"""
Scam Shield - Deterministic Rule Engine
Analyzes message content, sender info, URLs, phone numbers, UPI IDs, and amounts.
Detects scam indicators specific to the Indian threat landscape.
"""

from __future__ import annotations
import re
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urlparse


# Common Indian Brand Lookalike Targets and their legitimate canonical domains
INDIAN_BRANDS: Dict[str, List[str]] = {
    "sbi": ["sbi.co.in", "onlinesbi.sbi", "bank.sbi", "onlinesbi.com"],
    "hdfc": ["hdfcbank.com", "hdfc.com"],
    "icici": ["icicibank.com", "icicidirect.com"],
    "paytm": ["paytm.com", "paytmbank.com"],
    "phonepe": ["phonepe.com"],
    "amazon": ["amazon.in", "amazon.com"],
    "flipkart": ["flipkart.com"],
    "indiapost": ["indiapost.gov.in", "ippbonline.com"],
    "irctc": ["irctc.co.in"],
    "tneb": ["tangedco.gov.in", "tnebnet.org"],
    "axis": ["axisbank.com"],
    "pnb": ["pnbindia.in"],
    "kotak": ["kotak.com"],
    "gpay": ["google.com", "pay.google.com"],
    "bsnl": ["bsnl.co.in"],
    "jio": ["jio.com"],
    "airtel": ["airtel.in"],
}

# Suspicious TLDs heavily abused in Indian SMS & WhatsApp phishing campaigns
SUSPICIOUS_TLDS: Set[str] = {
    "xyz", "top", "click", "work", "club", "loan", "apk", "vip", "online",
    "rest", "buzz", "icu", "site", "link", "live", "info", "cam", "cyou",
    "shop", "tk", "ml", "ga", "cf", "gq", "gdn", "support", "cc", "kim",
    "today", "space", "best", "monster", "cfd"
}

# Known URL shorteners often used to mask malicious landing pages
URL_SHORTENERS: Set[str] = {
    "bit.ly", "tinyurl.com", "is.gd", "t.co", "rb.gy", "cutt.ly", "tiny.cc",
    "ow.ly", "shorturl.at", "bl.ink", "rebrand.ly", "v.gd", "soo.gd", "s.id"
}

# Genuine Bank Sender ID Prefix/Suffix patterns (e.g. AX-HDFCBK, VK-SBIINB, AD-ICICIB)
GENUINE_BANK_SENDER_PATTERNS = [
    r"^[A-Z]{2}-[A-Z0-9]{5,8}$",   # Telecom regulatory sender ID format: XX-BANKNAME
    r"^[A-Z]{2}[A-Z0-9]{5,8}$",    # Variant without hyphen: VKHDFCBK
]


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class RuleEngine:
    """
    Deterministic rule engine that inspects messages for Indian cyber scam patterns.
    Produces structured findings, detected entities, and a normalized risk score (0-100).
    """

    def __init__(self) -> None:
        # Regex patterns for entity extraction
        self.url_regex = re.compile(
            r"(?:https?://|www\.)[^\s/$.?#].[^\s]*",
            re.IGNORECASE
        )
        self.ip_url_regex = re.compile(
            r"https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?",
            re.IGNORECASE
        )
        self.upi_regex = re.compile(
            r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b"
        )
        # Indian mobile and landline regex: +91, 0, or 10-digit starting with 6-9
        self.phone_regex = re.compile(
            r"(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}|\b[6-9]\d{9}\b"
        )
        # Indian currency patterns: ₹ 500, Rs. 10,000, 25 Lakh, etc.
        self.amount_regex = re.compile(
            r"(?:₹|Rs\.?|INR)\s?[\d,]+(?:\.\d{1,2})?(?:\s?(?:lakh|crore|k|thousand))?|"
            r"\b\d+[\d,]*\s?(?:lakh|crore)\b",
            re.IGNORECASE
        )

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extracts URLs, phone numbers, UPI IDs, and currency amounts."""
        # Find URLs
        raw_urls = self.url_regex.findall(text)
        urls: List[str] = []
        for u in raw_urls:
            cleaned = u.rstrip(".,;!?:)'\"")
            if cleaned not in urls:
                urls.append(cleaned)

        # Find phone numbers
        raw_phones = self.phone_regex.findall(text)
        phones: List[str] = []
        for p in raw_phones:
            cleaned = re.sub(r"[\s-]", "", p)
            if cleaned.startswith("+91"):
                cleaned = cleaned[3:]
            elif cleaned.startswith("0") and len(cleaned) == 11:
                cleaned = cleaned[1:]
            if len(cleaned) == 10 and cleaned not in phones:
                phones.append(cleaned)

        # Find UPI IDs
        raw_upis = self.upi_regex.findall(text)
        # Filter out common email domains that are not UPI handles
        common_emails = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}
        upis: List[str] = [
            u for u in raw_upis
            if not any(u.lower().endswith("@" + domain) for domain in common_emails)
        ]

        # Find Amounts
        raw_amounts = self.amount_regex.findall(text)
        amounts: List[str] = [a.strip() for a in raw_amounts if a.strip()]

        return {
            "urls": urls,
            "phones": phones,
            "upi_ids": list(set(upis)),
            "amounts": list(set(amounts)),
        }

    def analyze_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Examines extracted URLs for phishing indicators and brand impersonation."""
        findings: List[Dict[str, Any]] = []

        for url in urls:
            normalized_url = url if url.startswith(("http://", "https://")) else "http://" + url
            parsed = urlparse(normalized_url)
            hostname = (parsed.hostname or "").lower()
            path = parsed.path.lower()

            # 1. IP address in URL host
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
                findings.append({
                    "rule_id": "URL_IP_HOST",
                    "description": f"URL uses raw IP address instead of domain name: {hostname}",
                    "weight": 25,
                    "category": "PHISHING_LINK"
                })

            # 2. Punycode / Internationalized Domain Name (IDN homograph attack)
            if "xn--" in hostname:
                findings.append({
                    "rule_id": "URL_PUNYCODE",
                    "description": f"Punycode domain detected (possible homograph spoofing): {hostname}",
                    "weight": 30,
                    "category": "PHISHING_LINK"
                })

            # 3. URL Shortener detection
            if hostname in URL_SHORTENERS or any(hostname.endswith("." + s) for s in URL_SHORTENERS):
                findings.append({
                    "rule_id": "URL_SHORTENER",
                    "description": f"Shortened link used to conceal final destination: {hostname}",
                    "weight": 15,
                    "category": "PHISHING_LINK"
                })

            # 4. Suspicious or high-risk TLD
            parts = hostname.split(".")
            if len(parts) >= 2:
                tld = parts[-1]
                if tld in SUSPICIOUS_TLDS:
                    findings.append({
                        "rule_id": "URL_SUSPICIOUS_TLD",
                        "description": f"Domain uses high-risk, low-cost TLD commonly used in phishing (.{tld})",
                        "weight": 20,
                        "category": "PHISHING_LINK"
                    })

            # 5. Insecure HTTP link asking for sensitive actions
            if url.startswith("http://"):
                findings.append({
                    "rule_id": "URL_INSECURE_HTTP",
                    "description": "Insecure HTTP protocol used instead of encrypted HTTPS",
                    "weight": 10,
                    "category": "PHISHING_LINK"
                })

            # 6. APK download link
            if path.endswith(".apk") or "download.apk" in path or ".apk?" in url.lower():
                findings.append({
                    "rule_id": "URL_APK_DOWNLOAD",
                    "description": "Direct Android APK download link detected (high malware/rat risk)",
                    "weight": 35,
                    "category": "LOAN_APP"
                })

            # 7. Indian Brand Lookalike Domain Detection (Levenshtein + Substring check)
            for brand, legit_domains in INDIAN_BRANDS.items():
                is_legit = any(hostname == ld or hostname.endswith("." + ld) for ld in legit_domains)
                if is_legit:
                    continue  # Verified canonical domain

                # Check if brand appears in hostname or path
                domain_core = parts[-2] if len(parts) >= 2 else hostname
                # Check for brand containment e.g. "sbi-kyc-portal.com" or "paytm-cashback"
                if brand in hostname:
                    findings.append({
                        "rule_id": "BRAND_IMPERSONATION_SUBSTRING",
                        "description": f"Brand '{brand.upper()}' impersonated in suspicious domain: {hostname}",
                        "weight": 30,
                        "category": "KYC_BANK"
                    })
                    break

                # Check Levenshtein distance against brand name for typo-squatting (e.g. 'sbii', 'hdfcbankk', 'icic1')
                dist = levenshtein_distance(domain_core, brand)
                if dist in (1, 2) and len(domain_core) >= 3:
                    findings.append({
                        "rule_id": "BRAND_TYPOSQUAT",
                        "description": f"Typo-squatted domain '{domain_core}' closely resembles official brand '{brand.upper()}' (edit distance: {dist})",
                        "weight": 30,
                        "category": "KYC_BANK"
                    })
                    break

        return findings

    def analyze_text(self, text: str, sender: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyzes text semantics, keywords, and sender ID for Indian cyber scam vectors."""
        findings: List[Dict[str, Any]] = []
        lower = text.lower()

        # 1. Electricity / Utility disconnection scam
        electricity_patterns = [
            r"electricity\s+(?:power\s+)?(?:bill|supply)",
            r"(?:power|electric|current|line)\s+(?:supply\s+)?(?:will\s+be\s+|has\s+been\s+)?disconnect(?:ed)?",
            r"(?:disconnect|cut off)\s+(?:at\s+)?(?:9:?30|8:?30|tonight|today|evening)",
            r"(?:contact|call)\s+(?:electricity\s+)?officer",
            r"tneb\s+(?:bill|power)",
            r"bijli\s+bill"
        ]
        if any(re.search(p, lower) for p in electricity_patterns):
            findings.append({
                "rule_id": "UTILITY_ELECTRICITY_DISCONNECTION",
                "description": "Urgent electricity/utility bill disconnection threat detected",
                "weight": 40,
                "category": "UTILITY_BILL"
            })

        # 2. Digital Arrest / Law Enforcement Extortion (CBI, Police, Narcotics, Customs)
        digital_arrest_patterns = [
            r"digital\s+arrest",
            r"(?:cbi|crime\s+branch|narcotics\s+control\s+bureau|ncb|mha|police)\s+(?:investigation|department|officer|notice)",
            r"(?:illegal|seized)\s+(?:parcel|drugs|mdma|passport)",
            r"(?:supreme\s+court|high\s+court)\s+(?:warrant|arrest\s+order)",
            r"stay\s+on\s+(?:skype|video\s+call)",
            r"aadhaar\s+(?:used\s+in|involved\s+in)\s+money\s+laundering",
            r"(?:parcel|courier)\s+(?:has\s+been\s+)?seized.*drugs"
        ]
        if any(re.search(p, lower) for p in digital_arrest_patterns):
            findings.append({
                "rule_id": "DIGITAL_ARREST_EXTORTION",
                "description": "Digital arrest or fake law enforcement intimidation detected",
                "weight": 55,
                "category": "DIGITAL_ARREST"
            })

        # 3. Bank Account / KYC / PAN suspension threats
        kyc_patterns = [
            r"kyc\s+(?:is\s+)?(?:suspended|expired|blocked|incomplete|pending)",
            r"pending\s+kyc",
            r"(?:update|link)\s+your\s+(?:pan|aadhaar|kyc)",
            r"(?:account|debit\s+card|netbanking|yono)\s+(?:has\s+been\s+|is\s+|will\s+be\s+)?(?:suspended|blocked|deactivated)",
            r"(?:click\s+here\s+to\s+)?unblock",
            r"sbi\s+yono\s+(?:blocked|suspended)",
            r"e-?kyc\s+(?:mandatory|update)"
        ]
        if any(re.search(p, lower) for p in kyc_patterns):
            findings.append({
                "rule_id": "KYC_ACCOUNT_SUSPENSION",
                "description": "Fake bank KYC/PAN update or account blocking threat detected",
                "weight": 35,
                "category": "KYC_BANK"
            })

        # 4. OTP / Sensitive Credential Harvest requests
        otp_patterns = [
            r"(?:share|send|tell|provide)\s+(?:your\s+)?(?:otp|one\s+time\s+password|pin|cvv)",
            r"forward\s+this\s+sms\s+to",
            r"6[\s-]digit\s+(?:code|verification\s+code)"
        ]
        if any(re.search(p, lower) for p in otp_patterns):
            findings.append({
                "rule_id": "OTP_CREDENTIAL_HARVEST",
                "description": "Direct request for OTP, PIN, CVV, or SMS forwarding detected",
                "weight": 40,
                "category": "KYC_BANK"
            })

        # 5. Work-from-home / Like & Subscribe / Telegram task jobs
        job_task_patterns = [
            r"telegram\s+(?:task|channel|group|job)",
            r"like\s+(?:youtube\s+videos?|google\s+reviews?|hotels?)\s+(?:earn|get)",
            r"part-?time\s+job.*earn\s+(?:₹|rs\.?|inr)?\s*\d{3,5}\s*(?:daily|per\s+day)",
            r"earn\s+\d{3,5}\s*(?:to|-)\s*\d{3,5}\s*(?:daily|per\s+day|every\s+day)",
            r"daily\s+income.*home\s+work",
            r"prepaid\s+task\s+payout"
        ]
        if any(re.search(p, lower) for p in job_task_patterns):
            findings.append({
                "rule_id": "JOB_TASK_TELEGRAM_FRAUD",
                "description": "Work-from-home YouTube review/Telegram prepaid task fraud pattern",
                "weight": 35,
                "category": "JOB_TASK"
            })

        # 6. Courier / Customs / Parcel seized scams
        courier_patterns = [
            r"(?:fedex|dhl|india\s+post|bluedart)\s+notice",
            r"(?:parcel|package|shipment|courier)\s+(?:has\s+been\s+)?(?:held|stopped|seized|stuck)",
            r"(?:parcel|shipment)\s+(?:held\s+at|in|at)\s+(?:customs|mumbai\s+airport|delhi\s+airport)",
            r"pay\s+(?:customs|clearance|duty|courier)\s+(?:fee|charges|tax)",
            r"customs\s+(?:clearance|fee|officer)",
            r"illegal\s+items\s+found\s+in\s+parcel"
        ]
        if any(re.search(p, lower) for p in courier_patterns):
            findings.append({
                "rule_id": "PARCEL_CUSTOMS_SEIZURE",
                "description": "Fake courier parcel seizure or customs fee demand detected",
                "weight": 40,
                "category": "PARCEL_COURIER"
            })

        # 7. Lottery / Prize / KBC / Lucky Draw scams
        lottery_patterns = [
            r"(?:congratulations|congrats).*won\s+(?:₹|rs\.?|inr)?\s*[\d,]+\s*(?:lakh|crore)?",
            r"kbc\s+(?:lottery|lucky\s+draw|winner)",
            r"selected\s+(?:as\s+)?lucky\s+winner",
            r"claim\s+your\s+(?:prize|cash\s+reward|lottery)",
            r"won\s+(?:a\s+)?(?:car|tata\s+safari|iphone|cash\s+voucher)"
        ]
        if any(re.search(p, lower) for p in lottery_patterns):
            findings.append({
                "rule_id": "LOTTERY_KBC_PRIZE",
                "description": "Unsolicited lottery, prize winner, or KBC jackpot scam detected",
                "weight": 35,
                "category": "LOTTERY_PRIZE"
            })

        # 8. High Urgency Pressure Tactics
        urgency_patterns = [
            r"within\s+(?:24|12|2|1)\s*hours?",
            r"immediate(?:ly)?",
            r"last\s+(?:warning|chance|reminder)",
            r"account\s+will\s+be\s+permanently\s+closed",
            r"fir\s+will\s+be\s+lodged",
            r"police\s+case\s+registered",
            r"to\s+avoid\s+arrest"
        ]
        if any(re.search(p, lower) for p in urgency_patterns):
            findings.append({
                "rule_id": "HIGH_URGENCY_PRESSURE",
                "description": "Artificial urgency or intimidation intended to provoke panic",
                "weight": 20,
                "category": "OTHER"
            })

        # 9. Fake Instant Loan Apps
        loan_patterns = [
            r"(?:instant|pre-?approved)\s+loan\s+(?:of\s+)?(?:₹|rs\.?|inr)?\s*[\d,]+",
            r"zero\s+cibil\s+score\s+loan",
            r"disbursal\s+in\s+5\s+minutes",
            r"install\s+(?:app|apk|loan\s+app)\s+now",
            r"loan\s+pre-?approved"
        ]
        if any(re.search(p, lower) for p in loan_patterns):
            findings.append({
                "rule_id": "PREDATORY_LOAN_APP",
                "description": "Unsolicited predatory instant loan / no-CIBIL loan offer detected",
                "weight": 35,
                "category": "LOAN_APP"
            })

        # 10. Sender ID checks
        if sender:
            s_clean = sender.strip()
            # If message claims to be from a bank, but sender is a personal 10-digit mobile number
            bank_keywords = ["sbi", "hdfc", "icici", "axis", "pnb", "bank", "yono", "kyc"]
            is_bank_msg = any(kw in lower for kw in bank_keywords)
            is_personal_mobile = bool(re.match(r"^(?:\+91|0)?[6-9]\d{9}$", s_clean))
            is_genuine_header = any(re.match(p, s_clean, re.IGNORECASE) for p in GENUINE_BANK_SENDER_PATTERNS)

            if is_bank_msg and is_personal_mobile:
                findings.append({
                    "rule_id": "SENDER_PERSONAL_MOBILE_BANK_SPOOF",
                    "description": f"Official banking notice sent from a personal mobile number ({s_clean}) instead of an authorized telecom header",
                    "weight": 35,
                    "category": "KYC_BANK"
                })
            elif is_genuine_header:
                findings.append({
                    "rule_id": "SENDER_GENUINE_GOVT_BANK_HEADER",
                    "description": f"Sender header '{s_clean}' matches TRAI registered commercial/banking bulk SMS format",
                    "weight": -20,  # Negative weight reduces false positives for genuine alerts
                    "category": "NONE"
                })

        return findings

    def analyze_upi(self, text: str, upi_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyzes UPI collect scam patterns (e.g. entering PIN to receive money)."""
        findings: List[Dict[str, Any]] = []
        lower = text.lower()

        # UPI collect scam: Scam artists request money while telling victim they are receiving money
        collect_phrases = [
            r"enter\s+(?:your\s+)?(?:upi\s+)?pin\s+to\s+receive",
            r"accept\s+(?:collect\s+)?request\s+to\s+(?:get|receive|credit)",
            r"pay\s+request\s+for\s+refund",
            r"scan\s+qr(?:\s+code)?\s+to\s+receive\s+money",
            r"upi\s+cashback\s+credited.*accept"
        ]
        if any(re.search(p, lower) for p in collect_phrases):
            findings.append({
                "rule_id": "UPI_COLLECT_REVERSE_SCAM",
                "description": "Crucial UPI Rule: Entering UPI PIN ALWAYS deducts money; it is NEVER used to receive money or refunds",
                "weight": 40,
                "category": "UPI_COLLECT"
            })

        for vpa in upi_ids:
            v_lower = vpa.lower()
            # Suspicious handles pretending to be official support on generic third party handles
            if any(h in v_lower for h in ["refund", "helpdesk", "customercare", "support", "kyc"]):
                findings.append({
                    "rule_id": "UPI_SUSPICIOUS_HANDLE_NAME",
                    "description": f"Suspicious UPI VPA name attempting to mimic support: {vpa}",
                    "weight": 20,
                    "category": "UPI_COLLECT"
                })

        return findings

    def evaluate(self, text: str, sender: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs complete deterministic analysis pipeline on input text and optional sender.
        Returns:
            entities: extracted URLs, phones, UPIs, amounts
            findings: list of triggered rules with rule_id, description, weight, category
            rule_score: 0-100 normalized score
            preliminary_verdict: SCAM, SUSPICIOUS, or LIKELY_SAFE
            top_category: suspected scam category
        """
        entities = self.extract_entities(text)
        url_findings = self.analyze_urls(entities["urls"])
        text_findings = self.analyze_text(text, sender)
        upi_findings = self.analyze_upi(text, entities["upi_ids"])

        all_findings = url_findings + text_findings + upi_findings

        # Calculate rule score
        # Sum weights, bounded between 0 and 100
        raw_score = sum(f["weight"] for f in all_findings)
        rule_score = max(0, min(100, raw_score))

        # Determine preliminary category based on highest weighted category
        category_counts: Dict[str, int] = {}
        for f in all_findings:
            cat = f.get("category", "OTHER")
            if cat != "NONE":
                category_counts[cat] = category_counts.get(cat, 0) + f.get("weight", 0)

        top_category = "NONE"
        if category_counts:
            top_category = max(category_counts.items(), key=lambda item: item[1])[0]

        # Determine preliminary verdict
        has_critical_flag = any(f.get("weight", 0) >= 40 for f in all_findings)
        if rule_score >= 50 or (has_critical_flag and rule_score >= 40):
            verdict = "SCAM"
        elif rule_score >= 25:
            verdict = "SUSPICIOUS"
        else:
            verdict = "LIKELY_SAFE"

        return {
            "entities": entities,
            "findings": all_findings,
            "rule_score": rule_score,
            "preliminary_verdict": verdict,
            "top_category": top_category if verdict != "LIKELY_SAFE" else "NONE",
        }
