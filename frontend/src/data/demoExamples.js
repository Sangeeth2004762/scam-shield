/**
 * Realistic scam and genuine message examples for Scam Shield demonstration.
 * Includes 8 high-impact Indian scam scenarios and 2 genuine transactional alerts.
 */

export const DEMO_EXAMPLES = [
  {
    id: "sbi_kyc",
    title: "Fake SBI YONO KYC Update",
    category: "KYC_BANK",
    badge: "Phishing SMS",
    sender: "+91 98234 11204",
    text: "Dear SBI customer, your YONO account has been suspended today due to pending KYC update. Click http://sbi-kyc-verify.xyz to update your PAN and unblock your netbanking immediately within 24 hours.",
    expectedVerdict: "SCAM",
    description: "Classic bank impersonation using fake urgent account suspension and suspicious .xyz domain."
  },
  {
    id: "electricity_bill",
    title: "Electricity Power Disconnection Threat",
    category: "UTILITY_BILL",
    badge: "Extortion SMS",
    sender: "+91 94321 88765",
    text: "Dear Consumer, Your Electricity power supply will be disconnected at 9:30 PM tonight because your previous month bill was not updated. Please immediately contact electricity officer at 9876543210. TNEB / Bijli Dept.",
    expectedVerdict: "SCAM",
    description: "Urgent night deadline pressure tactic designed to induce panic and force a direct phone call."
  },
  {
    id: "digital_arrest",
    title: "CBI / Police Digital Arrest Notice",
    category: "DIGITAL_ARREST",
    badge: "WhatsApp Intimidation",
    sender: "+91 70012 34567",
    text: "NOTICE: Crime Branch & CBI Investigation Dept. A parcel sent from Mumbai Airport containing 500g MDMA narcotics and fake passports was seized under your Aadhaar card. Supreme Court arrest warrant issued. Connect to Skype video call immediately for digital interrogation to avoid police raid.",
    expectedVerdict: "SCAM",
    description: "Fabricated law enforcement notice weaponizing 'Digital Arrest', which does not exist in Indian law."
  },
  {
    id: "fedex_customs",
    title: "FedEx / Customs Seizure Fee",
    category: "PARCEL_COURIER",
    badge: "Courier Fraud",
    sender: "+91 88901 23456",
    text: "FedEx Courier Alert: Your international shipment #FX-88921 is placed on hold by Customs at New Delhi Airport. Pay mandatory clearance customs duty of Rs. 18,500 within 2 hours to avoid parcel seizure and police notice.",
    expectedVerdict: "SCAM",
    description: "Demanding direct fee payments to personal accounts or UPI for alleged airport customs clearance."
  },
  {
    id: "telegram_task",
    title: "Work-From-Home YouTube Like Task",
    category: "JOB_TASK",
    badge: "Telegram Task Scam",
    sender: "+91 99887 66554",
    text: "Part-time job from home! Like YouTube videos & give 5-star Google ratings to earn Rs. 3,500 to Rs. 8,000 daily. Direct UPI payout every evening. Join Telegram channel: https://t.me/daily-income-tasks now to start your first task.",
    expectedVerdict: "SCAM",
    description: "Lucrative daily income promise for low-effort tasks leading to high-loss prepaid cryptocurrency scams."
  },
  {
    id: "kbc_lottery",
    title: "KBC 25 Lakh Lucky Draw Jackpot",
    category: "LOTTERY_PRIZE",
    badge: "Lottery Scam",
    sender: "+91 97112 33445",
    text: "Dear winner, Congratulations! Your mobile number won Rs. 25,00,000 cash prize in All India KBC Lucky Draw 2026. Send your bank account details and Rs. 4,500 tax registration fee to WhatsApp manager at 9845012345 to claim cheque.",
    expectedVerdict: "SCAM",
    description: "Advance fee fraud demanding an upfront 'processing/tax fee' for non-existent lottery winnings."
  },
  {
    id: "instant_loan_apk",
    title: "Predatory Instant Loan APK App",
    category: "LOAN_APP",
    badge: "Malicious APK",
    sender: "+91 81234 56789",
    text: "Instant pre-approved personal loan of Rs. 3,00,000 credited in 5 minutes! Zero CIBIL score needed, zero documentation. Download and install official loan app: https://speedycash.top/instant-loan.apk",
    expectedVerdict: "SCAM",
    description: "Distributes malware/spyware APK bypassing Google Play Store to harvest user contacts and blackmail."
  },
  {
    id: "upi_collect",
    title: "PhonePe / GPay Cashback Collect Request",
    category: "UPI_COLLECT",
    badge: "UPI Collect Reverse",
    sender: "+91 96543 21098",
    text: "Congratulations! You have received a cashback reward of Rs. 2,999 on PhonePe. Click accept and enter your UPI PIN to claim money directly into your bank account.",
    expectedVerdict: "SCAM",
    description: "Deceives user into entering their UPI PIN under the false premise of 'receiving' money."
  },
  {
    id: "genuine_bank_otp",
    title: "Genuine HDFC Bank OTP Transaction",
    category: "NONE",
    badge: "Genuine Banking SMS",
    sender: "VK-HDFCBK",
    text: "482910 is your OTP for purchase of Rs. 3,450.00 at AMAZON INDIA on HDFC Bank Card ending 4091. Valid for 10 minutes. Do not share OTP with anyone, including bank staff.",
    expectedVerdict: "LIKELY_SAFE",
    description: "Legitimate bank notification sent from registered telecom header with safety warning not to share."
  },
  {
    id: "genuine_amazon_delivery",
    title: "Genuine Amazon Delivery Dispatch",
    category: "NONE",
    badge: "Genuine Delivery Alert",
    sender: "AD-AMAZON",
    text: "Your Amazon order #408-9821345-1234567 is out for delivery with driver Ramesh. Share delivery PIN 6301 upon arrival. Track package live at https://amazon.in/orders.",
    expectedVerdict: "LIKELY_SAFE",
    description: "Standard delivery notification with official amazon.in domain and local delivery PIN."
  }
];
