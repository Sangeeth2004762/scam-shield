"""
Unit tests for Scam Shield Rule Engine (backend/rules.py).
Validates detection of Indian cyber scam patterns, lookalikes, entity extraction,
and verifies zero/low false-positives for genuine transactional messages.
"""

import pytest
from backend.rules import RuleEngine, levenshtein_distance


@pytest.fixture
def engine() -> RuleEngine:
    return RuleEngine()


def test_levenshtein_distance():
    assert levenshtein_distance("sbi", "sbi") == 0
    assert levenshtein_distance("sbi", "sb1") == 1
    assert levenshtein_distance("hdfc", "hdfcbank") == 4
    assert levenshtein_distance("icici", "icic1") == 1


def test_kyc_suspension_with_suspicious_tld(engine: RuleEngine):
    msg = "Dear SBI User, your YONO account has been suspended due to pending KYC. Click http://sbi-kyc-update.xyz to unblock within 24 hours."
    res = engine.evaluate(msg, sender="+919876543210")
    assert res["preliminary_verdict"] == "SCAM"
    assert res["top_category"] == "KYC_BANK"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "KYC_ACCOUNT_SUSPENSION" in rule_ids
    assert "URL_SUSPICIOUS_TLD" in rule_ids
    assert "BRAND_IMPERSONATION_SUBSTRING" in rule_ids
    assert "SENDER_PERSONAL_MOBILE_BANK_SPOOF" in rule_ids


def test_electricity_disconnection_threat(engine: RuleEngine):
    msg = "Dear consumer, your electricity power supply will be disconnected at 9:30 tonight because your previous month bill was not updated. Please immediately contact electricity officer at 9876543210."
    res = engine.evaluate(msg)
    assert res["preliminary_verdict"] in ("SCAM", "SUSPICIOUS")
    assert res["top_category"] == "UTILITY_BILL"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "UTILITY_ELECTRICITY_DISCONNECTION" in rule_ids
    assert "9876543210" in res["entities"]["phones"]


def test_digital_arrest_extortion(engine: RuleEngine):
    msg = "This is CBI Investigation Department notice. An illegal parcel containing narcotics and MDMA was seized at Mumbai airport under your Aadhaar. Digital arrest warrant issued by Supreme Court. Stay on Skype call immediately."
    res = engine.evaluate(msg)
    assert res["preliminary_verdict"] == "SCAM"
    assert res["top_category"] == "DIGITAL_ARREST"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "DIGITAL_ARREST_EXTORTION" in rule_ids


def test_job_task_telegram_scam(engine: RuleEngine):
    msg = "Part-time job offer! Like YouTube videos and earn Rs. 3000 to 5000 daily from home. Join our Telegram channel https://t.me/taskincome for instant daily payout."
    res = engine.evaluate(msg)
    assert res["preliminary_verdict"] in ("SCAM", "SUSPICIOUS")
    assert res["top_category"] == "JOB_TASK"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "JOB_TASK_TELEGRAM_FRAUD" in rule_ids


def test_courier_customs_seizure(engine: RuleEngine):
    msg = "FedEx notice: Your international parcel has been seized by customs at Delhi airport due to illegal items. Pay customs clearance fee of Rs 14,500 immediately to avoid arrest."
    res = engine.evaluate(msg)
    assert res["preliminary_verdict"] == "SCAM"
    assert res["top_category"] == "PARCEL_COURIER"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "PARCEL_CUSTOMS_SEIZURE" in rule_ids
    assert any("14,500" in amt for amt in res["entities"]["amounts"])


def test_kbc_lottery_prize(engine: RuleEngine):
    msg = "Congratulations! Your mobile number has won Rs. 25 Lakh in KBC Lucky Draw 2026. To claim your cash prize, contact manager at 9845012345."
    res = engine.evaluate(msg)
    assert res["preliminary_verdict"] in ("SCAM", "SUSPICIOUS")
    assert res["top_category"] == "LOTTERY_PRIZE"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "LOTTERY_KBC_PRIZE" in rule_ids


def test_apk_loan_download_link(engine: RuleEngine):
    msg = "Instant loan pre-approved for Rs 2,00,000 with zero CIBIL score! Install app immediately: https://fastcash.top/loan-app.apk"
    res = engine.evaluate(msg)
    assert res["preliminary_verdict"] == "SCAM"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "URL_APK_DOWNLOAD" in rule_ids
    assert "PREDATORY_LOAN_APP" in rule_ids


def test_upi_collect_reverse_fraud(engine: RuleEngine):
    msg = "Congratulations! Cashback of Rs 1,500 approved on PhonePe. Click accept and enter your UPI PIN to receive money in your bank account."
    res = engine.evaluate(msg)
    assert res["preliminary_verdict"] == "SCAM"
    assert res["top_category"] == "UPI_COLLECT"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "UPI_COLLECT_REVERSE_SCAM" in rule_ids


def test_ip_address_url(engine: RuleEngine):
    msg = "Your netbanking profile has expired. Re-authenticate now at http://192.168.1.105/auth before account blocked."
    res = engine.evaluate(msg)
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "URL_IP_HOST" in rule_ids


def test_punycode_homograph_spoof(engine: RuleEngine):
    msg = "Update security settings at https://xn--paytm-kba.com/verify now."
    res = engine.evaluate(msg)
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "URL_PUNYCODE" in rule_ids


def test_url_shortener_detection(engine: RuleEngine):
    msg = "Special reward waiting! Click https://bit.ly/3xY9kL2 to claim now."
    res = engine.evaluate(msg)
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "URL_SHORTENER" in rule_ids


def test_typosquatting_brand(engine: RuleEngine):
    msg = "Security alert from HDFC: verify credentials at http://hdfcbankk.com/login."
    res = engine.evaluate(msg)
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert any(r in rule_ids for r in ["BRAND_TYPOSQUAT", "BRAND_IMPERSONATION_SUBSTRING"])


def test_otp_harvest_request(engine: RuleEngine):
    msg = "Bank verification officer: please share OTP sent to your phone to complete pending verification."
    res = engine.evaluate(msg)
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "OTP_CREDENTIAL_HARVEST" in rule_ids


def test_suspicious_upi_handle(engine: RuleEngine):
    msg = "Pay 50 rupees processing fee to sbi-refund-helpdesk@okhdfcbank to claim tax refund."
    res = engine.evaluate(msg)
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "UPI_SUSPICIOUS_HANDLE_NAME" in rule_ids
    assert "sbi-refund-helpdesk@okhdfcbank" in res["entities"]["upi_ids"]


def test_genuine_bank_otp_message(engine: RuleEngine):
    # Genuine bank transactional SMS with TRAI header VK-HDFCBK
    msg = "458921 is your OTP for purchase of Rs. 4,250.00 at AMAZON INDIA on HDFC Bank Card ending 1234. Do not share OTP with anyone including bank staff."
    res = engine.evaluate(msg, sender="VK-HDFCBK")
    assert res["preliminary_verdict"] == "LIKELY_SAFE"
    assert res["rule_score"] < 25
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "SENDER_GENUINE_GOVT_BANK_HEADER" in rule_ids


def test_genuine_delivery_update(engine: RuleEngine):
    # Genuine delivery notification with legit domain
    msg = "Your Amazon order #402-1234567-8901234 has been dispatched and is out for delivery. Track package at https://amazon.in/orders. Share delivery code 4492 with driver upon arrival."
    res = engine.evaluate(msg, sender="AD-AMAZON")
    assert res["preliminary_verdict"] == "LIKELY_SAFE"
    assert res["rule_score"] < 25


def test_entity_extraction_comprehensive(engine: RuleEngine):
    text = "Visit https://fake-site.com and call +91 9845123456 or send Rs. 2,500 to payment-merchant@upi"
    entities = engine.extract_entities(text)
    assert "https://fake-site.com" in entities["urls"]
    assert "9845123456" in entities["phones"]
    assert "payment-merchant@upi" in entities["upi_ids"]
    assert any("2,500" in a for a in entities["amounts"])
