{
  "meta": {
    "version": "1.0",
    "note": "Simplified, curated dataset for a hackathon demo. Eligibility rules are condensed from official scheme guidelines and MUST be verified on the official portal before applying.",
    "fields": "rule.fixable = the user could plausibly change/close this gap (used for near-miss detection). specificity: 1 = broad scheme, 3 = tightly targeted. benefit_score: 1-10 relative size of benefit."
  },
  "schemes": [
    {
      "id": "pmegp",
      "name": "Prime Minister's Employment Generation Programme (PMEGP)",
      "short_name": "PMEGP",
      "category": "Entrepreneurship",
      "ministry": "Ministry of MSME (KVIC)",
      "benefit": "Credit-linked subsidy of 15%-35% of project cost for setting up a new micro-enterprise (project cost up to Rs 50 lakh for manufacturing, Rs 20 lakh for services).",
      "benefit_score": 9,
      "specificity": 3,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "entrepreneur", "label": "Entrepreneur / planning to start a business", "fixable": false, "hint": "PMEGP is meant for people setting up a new micro-enterprise."},
        {"field": "age", "op": "gte", "value": 18, "label": "Age 18 or above", "fixable": false, "hint": "Applicant must be at least 18 years old."},
        {"field": "business_stage", "op": "eq", "value": "new", "label": "Setting up a NEW venture (not an existing unit)", "fixable": true, "hint": "PMEGP funds only new units. If your business already runs, look at MUDRA for expansion loans."},
        {"field": "project_cost", "op": "lte", "value": 5000000, "label": "Project cost up to Rs 50 lakh (manufacturing) / Rs 20 lakh (service)", "fixable": true, "hint": "Scale down or phase the project so its cost stays within the PMEGP ceiling."}
      ],
      "documents": ["Aadhaar card", "PAN card", "Detailed Project Report (DPR)", "Caste / special-category certificate (if applicable)", "EDP training certificate (issued after enrolment)", "Bank account details", "Passport-size photograph", "Educational qualification proof"],
      "how_to_apply": "Register on the PMEGP e-portal, submit the online application with the project report, then complete the interview with the district task force and the bank.",
      "apply_url": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp"
    },
    {
      "id": "mudra",
      "name": "Pradhan Mantri MUDRA Yojana (PMMY)",
      "short_name": "MUDRA",
      "category": "Entrepreneurship",
      "ministry": "Ministry of Finance",
      "benefit": "Collateral-free business loans up to Rs 10 lakh: Shishu (up to Rs 50,000), Kishore (Rs 50,000 - Rs 5 lakh) and Tarun (Rs 5 lakh - Rs 10 lakh).",
      "benefit_score": 7,
      "specificity": 2,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "entrepreneur", "label": "Entrepreneur / small business owner", "fixable": false, "hint": "MUDRA loans are for non-farm small businesses and micro-enterprises."},
        {"field": "age", "op": "gte", "value": 18, "label": "Age 18 or above", "fixable": false, "hint": "Applicant must be an adult."},
        {"field": "project_cost", "op": "lte", "value": 1000000, "label": "Funding need up to Rs 10 lakh", "fixable": true, "hint": "MUDRA is capped at Rs 10 lakh. Reduce the first-phase funding need, or look at Stand-Up India / regular business loans for larger projects."}
      ],
      "documents": ["Aadhaar card", "PAN card", "Business address proof", "Quotation for machinery / stock to be purchased", "Passport-size photograph", "Last 6 months bank statement (existing businesses)", "Caste certificate (if applicable)"],
      "how_to_apply": "Apply at any bank, NBFC or microfinance institution, or online through the Udyamimitra portal.",
      "apply_url": "https://www.mudra.org.in"
    },
    {
      "id": "standup_india",
      "name": "Stand-Up India Scheme",
      "short_name": "Stand-Up India",
      "category": "Entrepreneurship",
      "ministry": "Department of Financial Services / SIDBI",
      "benefit": "Bank loans between Rs 10 lakh and Rs 1 crore for setting up a greenfield enterprise, reserved for women and SC/ST entrepreneurs.",
      "benefit_score": 9,
      "specificity": 3,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "entrepreneur", "label": "Entrepreneur / planning to start a business", "fixable": false, "hint": "Stand-Up India funds new enterprises in manufacturing, services or trading."},
        {"field": "age", "op": "gte", "value": 18, "label": "Age 18 or above", "fixable": false, "hint": "Applicant must be an adult."},
        {"any_of": [
          {"field": "gender", "op": "eq", "value": "female"},
          {"field": "category", "op": "in", "value": ["sc", "st"]}
        ], "label": "Woman entrepreneur OR belongs to SC / ST", "fixable": false, "hint": "This scheme is reserved for women and SC/ST entrepreneurs."},
        {"field": "business_stage", "op": "eq", "value": "new", "label": "Greenfield (first-time, new) enterprise", "fixable": true, "hint": "Only brand-new (greenfield) enterprises qualify."},
        {"field": "project_cost", "op": "between", "value": [1000000, 10000000], "label": "Loan requirement between Rs 10 lakh and Rs 1 crore", "fixable": true, "hint": "Stand-Up India loans start at Rs 10 lakh and go up to Rs 1 crore. For smaller needs, use MUDRA."}
      ],
      "documents": ["Aadhaar card", "PAN card", "Caste certificate (SC/ST applicants)", "Business plan / project report", "Address proof", "Bank statements", "Passport-size photograph"],
      "how_to_apply": "Apply through the Stand-Up Mitra portal or directly at a scheduled commercial bank branch.",
      "apply_url": "https://www.standupmitra.in"
    },
    {
      "id": "pm_kisan",
      "name": "PM Kisan Samman Nidhi (PM-KISAN)",
      "short_name": "PM-KISAN",
      "category": "Agriculture",
      "ministry": "Ministry of Agriculture & Farmers Welfare",
      "benefit": "Direct income support of Rs 6,000 per year, paid in three instalments of Rs 2,000 to the bank account.",
      "benefit_score": 6,
      "specificity": 3,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "farmer", "label": "Farmer", "fixable": false, "hint": "PM-KISAN is only for farmer families."},
        {"field": "land_ha", "op": "gt", "value": 0, "label": "Owns cultivable land registered in your name", "fixable": true, "hint": "PM-KISAN is paid to landholding farmer families. Get your land records updated (mutation) in your name to apply."}
      ],
      "documents": ["Aadhaar card (linked to bank account)", "Land ownership records (Khata / Khasra / Pattadar passbook)", "Bank passbook", "Mobile number linked to Aadhaar"],
      "how_to_apply": "Self-register on the PM-KISAN portal (Farmers Corner) or visit the nearest Common Service Centre / village revenue officer.",
      "apply_url": "https://pmkisan.gov.in"
    },
    {
      "id": "kcc",
      "name": "Kisan Credit Card (KCC)",
      "short_name": "Kisan Credit Card",
      "category": "Agriculture",
      "ministry": "Ministry of Agriculture / NABARD / Banks",
      "benefit": "Low-interest short-term crop credit with an interest subvention for timely repayment, plus accident insurance cover.",
      "benefit_score": 7,
      "specificity": 3,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "farmer", "label": "Farmer (owner, tenant or sharecropper)", "fixable": false, "hint": "KCC is for cultivators and allied-activity farmers."},
        {"field": "age", "op": "between", "value": [18, 75], "label": "Age between 18 and 75", "fixable": false, "hint": "KCC applicants must be between 18 and 75 years old (older applicants need a co-borrower)."}
      ],
      "documents": ["Aadhaar card", "PAN card (if available)", "Land records or tenancy agreement", "Passport-size photographs", "Crop pattern details", "Bank account details"],
      "how_to_apply": "Apply at your bank branch (cooperative, regional rural or commercial bank) or through the PM-KISAN KCC campaign at a Common Service Centre.",
      "apply_url": "https://www.myscheme.gov.in"
    },
    {
      "id": "post_matric_sc",
      "name": "Post-Matric Scholarship for Scheduled Castes",
      "short_name": "Post-Matric Scholarship (SC)",
      "category": "Education",
      "ministry": "Ministry of Social Justice & Empowerment",
      "benefit": "Reimbursement of compulsory fees plus a monthly maintenance allowance for SC students studying after Class 10.",
      "benefit_score": 8,
      "specificity": 3,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "student", "label": "Currently a student", "fixable": false, "hint": "Only for students enrolled in a recognised institution."},
        {"field": "category", "op": "eq", "value": "sc", "label": "Belongs to Scheduled Caste (SC)", "fixable": false, "hint": "This scholarship is for SC students only."},
        {"field": "education", "op": "in", "value": ["class_11_12", "diploma_iti", "undergraduate", "postgraduate"], "label": "Studying at post-matric level (Class 11 onwards)", "fixable": true, "hint": "Eligibility begins once you finish Class 10 and enrol in Class 11 or a higher course."},
        {"field": "income", "op": "lte", "value": 250000, "label": "Annual family income up to Rs 2.5 lakh", "fixable": true, "hint": "Family income must not exceed Rs 2.5 lakh per year. A fresh income certificate may help if your income has changed."}
      ],
      "documents": ["Caste certificate", "Income certificate", "Previous year marksheet", "Admission / fee receipt", "Aadhaar card", "Bank passbook (Aadhaar-seeded)", "Passport-size photograph"],
      "how_to_apply": "Register on the National Scholarship Portal (NSP), fill the application and submit it to your institution for verification.",
      "apply_url": "https://scholarships.gov.in"
    },
    {
      "id": "post_matric_st",
      "name": "Post-Matric Scholarship for Scheduled Tribes",
      "short_name": "Post-Matric Scholarship (ST)",
      "category": "Education",
      "ministry": "Ministry of Tribal Affairs",
      "benefit": "Fee reimbursement plus maintenance allowance for ST students studying after Class 10.",
      "benefit_score": 8,
      "specificity": 3,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "student", "label": "Currently a student", "fixable": false, "hint": "Only for students enrolled in a recognised institution."},
        {"field": "category", "op": "eq", "value": "st", "label": "Belongs to Scheduled Tribe (ST)", "fixable": false, "hint": "This scholarship is for ST students only."},
        {"field": "education", "op": "in", "value": ["class_11_12", "diploma_iti", "undergraduate", "postgraduate"], "label": "Studying at post-matric level (Class 11 onwards)", "fixable": true, "hint": "Eligibility begins once you finish Class 10 and enrol in Class 11 or a higher course."},
        {"field": "income", "op": "lte", "value": 250000, "label": "Annual family income up to Rs 2.5 lakh", "fixable": true, "hint": "Family income must not exceed Rs 2.5 lakh per year."}
      ],
      "documents": ["Tribe (ST) certificate", "Income certificate", "Previous year marksheet", "Admission / fee receipt", "Aadhaar card", "Bank passbook (Aadhaar-seeded)", "Passport-size photograph"],
      "how_to_apply": "Register on the National Scholarship Portal (NSP), fill the application and submit it to your institution for verification.",
      "apply_url": "https://scholarships.gov.in"
    },
    {
      "id": "pm_yasasvi",
      "name": "PM YASASVI Scholarship for OBC Students",
      "short_name": "PM YASASVI (OBC)",
      "category": "Education",
      "ministry": "Ministry of Social Justice & Empowerment",
      "benefit": "Annual scholarship support for meritorious OBC students in Classes 9-12 to cover education costs.",
      "benefit_score": 6,
      "specificity": 3,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "student", "label": "Currently a student", "fixable": false, "hint": "Only for school students."},
        {"field": "category", "op": "eq", "value": "obc", "label": "Belongs to OBC category", "fixable": false, "hint": "This scholarship is for OBC / EBC / DNT students."},
        {"field": "education", "op": "in", "value": ["class_9_10", "class_11_12"], "label": "Studying in Class 9 to 12", "fixable": true, "hint": "This scheme covers school-level education (Classes 9-12) only."},
        {"field": "income", "op": "lte", "value": 250000, "label": "Annual family income up to Rs 2.5 lakh", "fixable": true, "hint": "Family income must not exceed Rs 2.5 lakh per year."}
      ],
      "documents": ["OBC caste certificate", "Income certificate", "Previous marksheet", "School bonafide / admission proof", "Aadhaar card", "Bank passbook"],
      "how_to_apply": "Apply through the National Scholarship Portal during the annual application window.",
      "apply_url": "https://scholarships.gov.in"
    },
    {
      "id": "csss_college",
      "name": "Central Sector Scholarship for College & University Students",
      "short_name": "Central Sector Scholarship",
      "category": "Education",
      "ministry": "Department of Higher Education, Ministry of Education",
      "benefit": "Merit-based scholarship of about Rs 12,000 per year at graduation level (about Rs 20,000 per year at postgraduate level) toward living expenses.",
      "benefit_score": 6,
      "specificity": 2,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "student", "label": "Currently a student", "fixable": false, "hint": "Only for regular college / university students."},
        {"field": "education", "op": "in", "value": ["undergraduate", "postgraduate"], "label": "Pursuing a regular degree (UG / PG)", "fixable": true, "hint": "This scheme is for students in regular undergraduate or postgraduate courses."},
        {"field": "marks", "op": "gte", "value": 80, "label": "Class 12 score in the top 20 percentile (about 80%+ used as a proxy)", "fixable": true, "hint": "The official cut-off is the 80th percentile of your Class 12 board. Check your board's percentile list."},
        {"field": "income", "op": "lte", "value": 450000, "label": "Annual family income up to Rs 4.5 lakh", "fixable": true, "hint": "Family income must not exceed Rs 4.5 lakh per year."}
      ],
      "documents": ["Class 12 marksheet", "Income certificate", "College admission / bonafide certificate", "Aadhaar card", "Bank passbook (Aadhaar-seeded)", "Passport-size photograph"],
      "how_to_apply": "Apply on the National Scholarship Portal (NSP) and get the application verified by your institute.",
      "apply_url": "https://scholarships.gov.in"
    },
    {
      "id": "pmkvy",
      "name": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
      "short_name": "PMKVY Skill Training",
      "category": "Skilling & Employment",
      "ministry": "Ministry of Skill Development & Entrepreneurship",
      "benefit": "Free short-term skill training with government-recognised certification and placement support.",
      "benefit_score": 5,
      "specificity": 3,
      "rules": [
        {"field": "occupation", "op": "eq", "value": "unemployed", "label": "Unemployed / job seeker", "fixable": false, "hint": "PMKVY short-term training targets job seekers and school / college dropouts."},
        {"field": "age", "op": "between", "value": [15, 45], "label": "Age between 15 and 45", "fixable": false, "hint": "PMKVY training is open to ages 15-45."}
      ],
      "documents": ["Aadhaar card", "Bank account details", "Highest education certificate", "Passport-size photograph"],
      "how_to_apply": "Find a nearby training centre on the Skill India Digital portal and enrol for a job role of your choice.",
      "apply_url": "https://www.skillindiadigital.gov.in"
    },
    {
      "id": "ayushman_vay_vandana",
      "name": "Ayushman Vay Vandana Card (PM-JAY for 70+)",
      "short_name": "Ayushman Vay Vandana",
      "category": "Health & Social Security",
      "ministry": "National Health Authority",
      "benefit": "Free health insurance cover of up to Rs 5 lakh per year for all senior citizens aged 70 and above, regardless of income.",
      "benefit_score": 8,
      "specificity": 3,
      "rules": [
        {"field": "age", "op": "gte", "value": 70, "label": "Age 70 years or above", "fixable": false, "hint": "This card is for senior citizens aged 70 and above."}
      ],
      "documents": ["Aadhaar card", "Mobile number", "Address proof"],
      "how_to_apply": "Enrol through the Ayushman App or the Beneficiary portal, or at an empanelled hospital / Common Service Centre.",
      "apply_url": "https://beneficiary.nha.gov.in"
    },
    {
      "id": "apy",
      "name": "Atal Pension Yojana (APY)",
      "short_name": "Atal Pension Yojana",
      "category": "Health & Social Security",
      "ministry": "PFRDA / Ministry of Finance",
      "benefit": "Guaranteed monthly pension of Rs 1,000 to Rs 5,000 from age 60, depending on contribution.",
      "benefit_score": 6,
      "specificity": 1,
      "rules": [
        {"field": "age", "op": "between", "value": [18, 40], "label": "Age between 18 and 40", "fixable": false, "hint": "APY enrolment is open only between ages 18 and 40."},
        {"field": "occupation", "op": "not_in", "value": ["salaried"], "label": "Not a salaried employee with statutory pension cover", "fixable": false, "hint": "Salaried employees usually have EPF / NPS coverage and are excluded. Please confirm with your bank."}
      ],
      "documents": ["Aadhaar card", "Savings bank account (auto-debit)", "Mobile number"],
      "how_to_apply": "Open the APY form at your bank / post office branch or through net banking.",
      "apply_url": "https://www.jansuraksha.gov.in"
    },
    {
      "id": "pmjjby",
      "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
      "short_name": "PM Jeevan Jyoti Bima",
      "category": "Health & Social Security",
      "ministry": "Ministry of Finance",
      "benefit": "Life insurance cover of Rs 2 lakh for a low annual premium (about Rs 436).",
      "benefit_score": 4,
      "specificity": 1,
      "rules": [
        {"field": "age", "op": "between", "value": [18, 50], "label": "Age between 18 and 50", "fixable": false, "hint": "Enrolment is open between ages 18 and 50."}
      ],
      "documents": ["Aadhaar card", "Savings bank account with auto-debit consent", "Nominee details"],
      "how_to_apply": "Enrol at your bank branch or via net / mobile banking; the premium is auto-debited each year.",
      "apply_url": "https://www.jansuraksha.gov.in"
    },
    {
      "id": "pmsby",
      "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
      "short_name": "PM Suraksha Bima",
      "category": "Health & Social Security",
      "ministry": "Ministry of Finance",
      "benefit": "Accidental death and disability insurance cover of Rs 2 lakh for a premium of only about Rs 20 per year.",
      "benefit_score": 4,
      "specificity": 1,
      "rules": [
        {"field": "age", "op": "between", "value": [18, 70], "label": "Age between 18 and 70", "fixable": false, "hint": "Enrolment is open between ages 18 and 70."}
      ],
      "documents": ["Aadhaar card", "Savings bank account with auto-debit consent", "Nominee details"],
      "how_to_apply": "Enrol at your bank branch or via net / mobile banking; the premium is auto-debited each year.",
      "apply_url": "https://www.jansuraksha.gov.in"
    }
  ]
}
