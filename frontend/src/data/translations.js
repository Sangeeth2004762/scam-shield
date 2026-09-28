/**
 * Multilingual UI translations for Scam Shield: English, Tamil (தமிழ்), Hindi (हिन्दी).
 */

export const TRANSLATIONS = {
  en: {
    appTitle: "Scam Shield",
    appTagline: "AI-Powered Scam Detector for Indian Citizens",
    appSub: "Instant risk assessment for SMS, WhatsApp & UPI scams in English, தமிழ் & हिन्दी",
    navHome: "Scanner",
    navInsights: "Insights & Stats",
    navHistory: "History",
    callHelpline: "Call 1930",

    // Input Card
    inputHeader: "Analyze Suspicious Message or Screenshot",
    inputSub: "Paste text from SMS, WhatsApp, Telegram, or upload a chat screenshot.",
    pastePlaceholder: "e.g., Dear customer, your electricity power supply will be disconnected at 9:30 tonight... OR Dear SBI user, your YONO account is blocked...",
    senderLabel: "Sender ID / Phone / URL (Optional)",
    senderPlaceholder: "e.g. +91 9876543210 or VK-SBIINB or http://...",
    uploadTab: "Screenshot Upload",
    textTab: "Paste Text",
    dropzoneTitle: "Drop screenshot here or click to browse",
    dropzoneSub: "Supports PNG, JPG, WEBP (Max 10MB)",
    privacyToggle: "Do not save this scan to public history",
    btnAnalyze: "Scan for Scam Threats",
    btnAnalyzing: "Analyzing with Gemini AI...",
    btnExamples: "Try Realistic Examples",
    btnClear: "Clear",

    // Result Card
    verdictScam: "CONFIRMED SCAM",
    verdictSuspicious: "SUSPICIOUS THREAT",
    verdictSafe: "LIKELY SAFE",
    riskScoreLabel: "Risk Assessment Score",
    ruleScoreLabel: "Rule Engine Score",
    llmScoreLabel: "Gemini AI Score",
    confidenceLabel: "Detection Confidence",
    categoryLabel: "Threat Category",
    redFlagsTitle: "Red Flags & Heuristics Triggered",
    explanationTitle: "Plain-Language Explanation",
    actionTitle: "What You Should Do Right Now",
    extractedTextTitle: "Text Extracted from Screenshot",
    entitiesFoundTitle: "Detected Threat Indicators",

    // Report Helper
    reportHeader: "Pre-filled Cybercrime Complaint Draft",
    reportSub: "Ready to copy and submit on the National Cyber Crime Reporting Portal or report to 1930.",
    btnCopyReport: "Copy Complaint Draft",
    btnCopied: "Copied to Clipboard!",
    btnCall1930: "Call 1930 Helpline",
    btnGovPortal: "cybercrime.gov.in",
    btnChakshu: "Chakshu / Sanchar Saathi",
    reportDisclaimer: "Scam Shield drafts this report to save you time. Never share your own OTPs or UPI PINs. Officially file this at cybercrime.gov.in or dial 1930.",

    // Insights
    insightsTitle: "National Cyber Threat Intelligence",
    insightsSub: "Aggregated statistics and trending scam vectors analyzed across India",
    totalScans: "Total Scans Analyzed",
    avgRisk: "Average Risk Score",
    highRiskScams: "High Risk Scams Detected",
    categoryBreakdown: "Scam Categories Breakdown",
    verdictDistribution: "Verdict Distribution",
    threatBriefingTitle: "Top Indian Scam Vectors",

    // Categories
    categories: {
      KYC_BANK: "Fake Bank KYC / Account Suspension",
      PARCEL_COURIER: "Customs / Courier Parcel Extortion",
      JOB_TASK: "Telegram / YouTube Like Job Fraud",
      LOAN_APP: "Predatory Instant Loan App",
      DIGITAL_ARREST: "Impersonation / Digital Arrest Extortion",
      UTILITY_BILL: "Electricity Bill Disconnection Threat",
      LOTTERY_PRIZE: "Lottery / KBC Prize Fraud",
      UPI_COLLECT: "UPI Collect Request / Fake Cashback",
      INVESTMENT_CRYPTO: "Stock / Crypto Investment Fraud",
      ROMANCE: "Romance / Matrimonial Extortion",
      PHISHING_LINK: "Phishing Link / Credential Theft",
      OTHER: "Suspicious Unsolicited Fraud",
      NONE: "Legitimate Communication"
    }
  },

  ta: {
    appTitle: "ஸ்கேம் ஷீல்ட் (Scam Shield)",
    appTagline: "இந்திய பயனர்களுக்கான ஏஐ மோசடி தடுப்பான்",
    appSub: "எஸ்எம்எஸ், வாட்ஸ்அப் மற்றும் யுபிஐ மோசடிகளை நொடியில் கண்டறிந்து தற்காத்துக் கொள்ளுங்கள்",
    navHome: "ஸ்கேனர்",
    navInsights: "புள்ளிவிவரங்கள்",
    navHistory: "வரலாறு",
    callHelpline: "1930-ல் அழைக்க",

    // Input Card
    inputHeader: "சந்தேகத்திற்கிடமான செய்தி அல்லது ஸ்கிரீன்ஷாட்டை ஆய்வு செய்க",
    inputSub: "எஸ்எம்எஸ், வாட்ஸ்அப் அல்லது டெலிகிராம் செய்தியை உள்ளிடவும் அல்லது ஸ்கிரீன்ஷாட்டை பதிவேற்றவும்.",
    pastePlaceholder: "எ.கா: மின் கட்டணம் செலுத்தாததால் இன்று இரவு 9:30 மணிக்கு மின் இணைப்பு துண்டிக்கப்படும்... அல்லது உங்கள் வங்கி கணக்கு முடக்கப்பட்டுள்ளது...",
    senderLabel: "அனுப்பியவர் எண் / தலைப்பு (விருப்பத்தேர்வு)",
    senderPlaceholder: "எ.கா: +91 9876543210 அல்லது VK-SBIINB",
    uploadTab: "ஸ்கிரீன்ஷாட் பதிவேற்றம்",
    textTab: "உரை உள்ளீடு",
    dropzoneTitle: "ஸ்கிரீன்ஷாட்டை இங்கே இழுத்து விடவும் அல்லது தேர்ந்தெடுக்கவும்",
    dropzoneSub: "PNG, JPG, WEBP ஆதரவு (அதிகபட்சம் 10MB)",
    privacyToggle: "இந்த பதிவை சேமிக்க வேண்டாம் (தனிநபர் பாதுகாப்பு)",
    btnAnalyze: "மோசடி உள்ளதா என சோதி",
    btnAnalyzing: "ஆய்வு செய்யப்படுகிறது...",
    btnExamples: "உதாரணங்களை பார்க்க",
    btnClear: "அழி",

    // Result Card
    verdictScam: "உறுதிசெய்யப்பட்ட மோசடி (SCAM)",
    verdictSuspicious: "சந்தேகத்திற்கிடமானது (SUSPICIOUS)",
    verdictSafe: "பாதுகாப்பானது (LIKELY SAFE)",
    riskScoreLabel: "அபாய மதிப்பீடு",
    ruleScoreLabel: "விதிமுறை மதிப்பெண்",
    llmScoreLabel: "ஏஐ மதிப்பெண்",
    confidenceLabel: "நம்பகத்தன்மை",
    categoryLabel: "மோசடி வகை",
    redFlagsTitle: "கண்டறியப்பட்ட எச்சரிக்கை குறிகள்",
    explanationTitle: "எளிய விளக்கம்",
    actionTitle: "நீங்கள் உடனடியாக செய்ய வேண்டியவை",
    extractedTextTitle: "படத்திலிருந்து எடுக்கப்பட்ட உரை",
    entitiesFoundTitle: "கண்டறியப்பட்ட விவரங்கள்",

    // Report Helper
    reportHeader: "தயாரிக்கப்பட்ட சைபர் கிரைம் புகார் வரைவு",
    reportSub: "cybercrime.gov.in போர்ட்டலில் புகாரளிக்க அல்லது 1930 உதவி எண்ணிற்கு வழங்க இதை நகலெடுக்கலாம்.",
    btnCopyReport: "புகார் வரைவை நகலெடு",
    btnCopied: "நகலெடுக்கப்பட்டது!",
    btnCall1930: "1930 உதவி எண்",
    btnGovPortal: "cybercrime.gov.in",
    btnChakshu: "சஞ்சார் சாதி / சக்ஷு (Chakshu)",
    reportDisclaimer: "ஸ்கேம் ஷீல்ட் உங்கள் நேரத்தை சேமிக்க இந்த வரைவை உருவாக்குகிறது. உங்கள் OTP அல்லது UPI பின்னை பகிர வேண்டாம். அதிகாரப்பூர்வமாக cybercrime.gov.in-ல் புகாரளிக்கவும்.",

    // Insights
    insightsTitle: "தேசிய சைபர் அச்சுறுத்தல் பகுப்பாய்வு",
    insightsSub: "இந்தியா முழுவதும் பதிவான மோசடிகளின் தொகுக்கப்பட்ட புள்ளிவிவரங்கள்",
    totalScans: "மொத்த சோதனைகள்",
    avgRisk: "சராசரி அபாய அளவு",
    highRiskScams: "கடுமையான மோசடிகள்",
    categoryBreakdown: "மோசடி பிரிவுகள்",
    verdictDistribution: "முடிவுகளின் விகிதம்",
    threatBriefingTitle: "முக்கிய இந்திய மோசடி உத்திகள்",

    // Categories
    categories: {
      KYC_BANK: "வங்கி கேஒய்சி / கணக்கு முடக்கம் மோசடி",
      PARCEL_COURIER: "சுங்கத்துறை / பார்சல் பறிமுதல் மோசடி",
      JOB_TASK: "டெலிகிராம் / பகுதிநேர வேலை மோசடி",
      LOAN_APP: "ஆபத்தான உடனடி கடன் ஆப்",
      DIGITAL_ARREST: "டிஜிட்டல் கைது / போலீஸ் மிரட்டல் மோசடி",
      UTILITY_BILL: "மின்கட்டண இணைப்பு துண்டிப்பு மோசடி",
      LOTTERY_PRIZE: "லாட்டரி / பரிசு வென்றதாக ஏமாற்றுதல்",
      UPI_COLLECT: "யுபிஐ பணம் வசூலிப்பு / போலி கேஷ்பேக்",
      INVESTMENT_CRYPTO: "பங்குச்சந்தை / கிரிப்டோ முதலீட்டு மோசடி",
      ROMANCE: "திருமண / காதல் பண பறிப்பு மோசடி",
      PHISHING_LINK: "போலி இணைப்பு / கடவுச்சொல் திருட்டு",
      OTHER: "பிற சந்தேகத்திற்குரிய மோசடி",
      NONE: "முறையான செய்தி"
    }
  },

  hi: {
    appTitle: "स्कैम शील्ड (Scam Shield)",
    appTagline: "भारतीय नागरिकों के लिए एआई-संचालित स्कैम डिटेक्टर",
    appSub: "एसएमएस, व्हाट्सएप और यूपीआई धोखाधड़ी की तुरंत पहचान करें और सुरक्षित रहें",
    navHome: "स्कैनर",
    navInsights: "आंकड़े व विश्लेषण",
    navHistory: "इतिहास",
    callHelpline: "1930 पर कॉल करें",

    // Input Card
    inputHeader: "संदिग्ध संदेश या स्क्रीनशॉट की जांच करें",
    inputSub: "एसएमएस, व्हाट्सएप, टेलीग्राम का टेक्स्ट पेस्ट करें या चैट का स्क्रीनशॉट अपलोड करें।",
    pastePlaceholder: "उदा: प्रिय उपभोक्ता, आपका बिजली कनेक्शन आज रात 9:30 बजे काट दिया जाएगा... या प्रिय ग्राहक, आपका बैंक खाता ब्लॉक हो गया है...",
    senderLabel: "भेजने वाले का नंबर / आईडी (वैकल्पिक)",
    senderPlaceholder: "उदा: +91 9876543210 या VK-SBIINB",
    uploadTab: "स्क्रीनशॉट अपलोड",
    textTab: "टेक्स्ट पेस्ट करें",
    dropzoneTitle: "स्क्रीनशॉट यहां ड्रैग करें या फाइल चुनें",
    dropzoneSub: "PNG, JPG, WEBP समर्थित (अधिकतम 10MB)",
    privacyToggle: "इस स्कैन को इतिहास में न सहेजें (गोपनीयता)",
    btnAnalyze: "धोखाधड़ी की जांच करें",
    btnAnalyzing: "जेमिनी एआई द्वारा विश्लेषण जारी...",
    btnExamples: "उदाहरण आज़माएं",
    btnClear: "साफ करें",

    // Result Card
    verdictScam: "पुष्टीकृत धोखाधड़ी (SCAM)",
    verdictSuspicious: "संदिग्ध गतिविधि (SUSPICIOUS)",
    verdictSafe: "संभवतः सुरक्षित (LIKELY SAFE)",
    riskScoreLabel: "जोखिम स्कोर",
    ruleScoreLabel: "नियम स्कोर",
    llmScoreLabel: "एआई स्कोर",
    confidenceLabel: "सटीकता विश्वास",
    categoryLabel: "धोखाधड़ी श्रेणी",
    redFlagsTitle: "पहचाने गए खतरे और चेतावनी संकेत",
    explanationTitle: "सरल भाषा में व्याख्या",
    actionTitle: "आपको तुरंत क्या कदम उठाने चाहिए",
    extractedTextTitle: "स्क्रीनशॉट से निकाला गया टेक्स्ट",
    entitiesFoundTitle: "पाए गए संदिग्ध पहचानकर्ता",

    // Report Helper
    reportHeader: "तैयार साइबर अपराध शिकायत प्रारूप",
    reportSub: "इसे कॉपी करके cybercrime.gov.in पर दर्ज करें या 1930 हेल्पलाइन पर विवरण दें।",
    btnCopyReport: "शिकायत ड्राफ्ट कॉपी करें",
    btnCopied: "कॉपी हो गया!",
    btnCall1930: "1930 हेल्पलाइन",
    btnGovPortal: "cybercrime.gov.in",
    btnChakshu: "चक्षु / संचार साथी",
    reportDisclaimer: "स्कैम शील्ड आपका समय बचाने के लिए यह शिकायत प्रारूप तैयार करता है। अपना ओटीपी या यूपीआई पिन कभी साझा न करें। आधिकारिक रूप से cybercrime.gov.in पर रिपोर्ट करें।",

    // Insights
    insightsTitle: "राष्ट्रीय साइबर खतरा विश्लेषण",
    insightsSub: "पूरे भारत में दर्ज साइबर धोखाधड़ी के आंकड़े और रुझान",
    totalScans: "कुल विश्लेषण किए गए स्कैन",
    avgRisk: "औसत जोखिम स्कोर",
    highRiskScams: "उच्च जोखिम वाले स्कैम",
    categoryBreakdown: "धोखाधड़ी श्रेणियों का विवरण",
    verdictDistribution: "निर्णय का वितरण",
    threatBriefingTitle: "भारत में सक्रिय प्रमुख स्कैम",

    // Categories
    categories: {
      KYC_BANK: "फर्जी बैंक केवाईसी / खाता ब्लॉक",
      PARCEL_COURIER: "कस्टम्स / कूरियर पार्सल जब्ती धोखाधड़ी",
      JOB_TASK: "टेलीग्राम / यूट्यूब लाइक टास्क फ्रॉड",
      LOAN_APP: "अवैध इंस्टेंट लोन ऐप",
      DIGITAL_ARREST: "फर्जी पुलिस / डिजिटल अरेस्ट वसूली",
      UTILITY_BILL: "बिजली बिल कनेक्शन कटने की धमकी",
      LOTTERY_PRIZE: "केबीसी लॉटरी / नकद पुरस्कार झांसा",
      UPI_COLLECT: "यूपीआई कलेक्ट रिक्वेस्ट / फर्जी कैशबैक",
      INVESTMENT_CRYPTO: "शेयर / क्रिप्टो निवेश पोंजी स्कीम",
      ROMANCE: "मैट्रिमोनियल / रोमांस जबरन वसूली",
      PHISHING_LINK: "फ़िशिंग लिंक / पासवर्ड चोरी",
      OTHER: "अन्य संदिग्ध अनचाही धोखाधड़ी",
      NONE: "प्रामाणिक वैध संदेश"
    }
  }
};
