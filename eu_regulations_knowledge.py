#!/usr/bin/env python3
"""
EU Regulations Knowledge Base - Fallback Data
Provides essential EU regulation information when SPARQL endpoint is not accessible.
"""

EU_REGULATIONS_DB = {
    "gdpr": {
        "title": "General Data Protection Regulation (EU) 2016/679",
        "celex": "32016R0679",
        "date": "2016-04-27",
        "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        "summary": "Regulation on the protection of natural persons with regard to the processing of personal data and on the free movement of such data",
        "key_principles": [
            "Lawful, fair and transparent processing",
            "Purpose limitation",
            "Data minimisation",
            "Accuracy",
            "Storage limitation",
            "Integrity and confidentiality",
            "Accountability"
        ],
        "key_articles": {
            "Article 6": "Lawfulness of processing",
            "Article 7": "Conditions for consent",
            "Article 13": "Information to be provided",
            "Article 17": "Right to erasure ('right to be forgotten')",
            "Article 25": "Data protection by design and by default"
        }
    },
    "ai_act": {
        "title": "Regulation (EU) 2024/1689 on artificial intelligence (AI Act)",
        "celex": "32024R1689",
        "date": "2024-06-13",
        "url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        "summary": "Regulation laying down harmonised rules on artificial intelligence",
        "risk_categories": [
            "Minimal risk AI systems",
            "Limited risk AI systems", 
            "High-risk AI systems",
            "Unacceptable risk AI systems"
        ],
        "high_risk_areas": [
            "Biometric identification and categorisation",
            "Management of critical infrastructure",
            "Education and vocational training",
            "Employment and worker management",
            "Access to essential services",
            "Law enforcement",
            "Migration, asylum and border control",
            "Administration of justice and democratic processes"
        ]
    },
    "dsa": {
        "title": "Digital Services Act (EU) 2022/2065",
        "celex": "32022R2065", 
        "date": "2022-10-19",
        "url": "https://eur-lex.europa.eu/eli/reg/2022/2065/oj",
        "summary": "Regulation on a Single Market For Digital Services",
        "scope": [
            "Intermediary services",
            "Hosting services", 
            "Online platforms",
            "Very large online platforms",
            "Very large online search engines"
        ],
        "obligations": [
            "Notice and action mechanisms",
            "Transparency reporting",
            "Risk management",
            "Content moderation",
            "Crisis response mechanisms"
        ]
    },
    "consumer_rights": {
        "title": "Consumer Rights Directive 2011/83/EU",
        "celex": "32011L0083",
        "date": "2011-10-25", 
        "url": "https://eur-lex.europa.eu/eli/dir/2011/83/oj",
        "summary": "Directive on consumer rights",
        "key_rights": [
            "Right of withdrawal",
            "Pre-contractual information requirements",
            "Delivery conditions",
            "Risk and ownership transfer",
            "Performance and remedies"
        ],
        "digital_content": [
            "Information requirements for digital content",
            "Right of withdrawal for digital content",
            "Performance of digital content contracts"
        ]
    },
    "eidas": {
        "title": "eIDAS Regulation (EU) No 910/2014",
        "celex": "32014R0910",
        "date": "2014-07-23",
        "url": "https://eur-lex.europa.eu/eli/reg/2014/910/oj", 
        "summary": "Regulation on electronic identification and trust services for electronic transactions",
        "services": [
            "Electronic signatures",
            "Electronic seals",
            "Time stamps",
            "Electronic delivery services",
            "Website authentication"
        ]
    }
}

COMPLIANCE_KEYWORDS = {
    "gdpr": [
        "personal data", "data processing", "consent", "privacy policy", 
        "data subject", "controller", "processor", "data protection",
        "user data", "customer data", "email addresses", "behavioral data"
    ],
    "ai_act": [
        "artificial intelligence", "machine learning", "algorithm", "automated decision",
        "ai system", "high-risk ai", "biometric", "automated processing",
        "neural network", "deep learning", "automated", "decision making"
    ],
    "dsa": [
        "digital services", "online platform", "social media", "content moderation",
        "hosting service", "intermediary service", "user-generated content",
        "content removal", "notice and takedown", "platform"
    ],
    "consumer_rights": [
        "consumer", "customer", "purchase", "product", "service", "marketplace",
        "e-commerce", "online sales", "digital content", "withdrawal", "refund"
    ],
    "eidas": [
        "electronic signature", "digital signature", "authentication", "trust service",
        "electronic identity", "digital certificate", "qualified signature"
    ]
}

def get_regulation_info(regulation_key: str) -> dict:
    """Get detailed information about a specific regulation"""
    return EU_REGULATIONS_DB.get(regulation_key, {})

def search_regulations_by_keywords(keywords: list) -> list:
    """Search regulations by keywords"""
    results = []
    keywords_lower = [k.lower() for k in keywords]
    
    for reg_key, reg_data in EU_REGULATIONS_DB.items():
        # Check if any keywords match this regulation
        reg_keywords = COMPLIANCE_KEYWORDS.get(reg_key, [])
        
        for keyword in keywords_lower:
            if any(keyword in reg_keyword.lower() for reg_keyword in reg_keywords):
                results.append({
                    "regulation": reg_key,
                    "title": reg_data["title"],
                    "celex": reg_data["celex"],
                    "date": reg_data["date"],
                    "url": reg_data["url"],
                    "summary": reg_data["summary"]
                })
                break
    
    return results

def detect_regulation_types(text: str) -> list:
    """Detect which regulation types are relevant to the given text"""
    text_lower = text.lower()
    detected = []
    
    for reg_type, keywords in COMPLIANCE_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            detected.append(reg_type)
    
    return detected

def get_compliance_suggestions(regulation_types: list, scenario: str) -> dict:
    """Get compliance suggestions based on detected regulation types"""
    suggestions = {
        "issues": [],
        "recommendations": [],
        "regulations": []
    }
    
    scenario_lower = scenario.lower()
    
    for reg_type in regulation_types:
        reg_info = get_regulation_info(reg_type)
        if reg_info:
            suggestions["regulations"].append(reg_info)
        
        # Add specific compliance checks
        if reg_type == "gdpr":
            if "personal data" in scenario_lower or "user data" in scenario_lower:
                if "consent" not in scenario_lower:
                    suggestions["issues"].append("Missing explicit consent mechanism for personal data processing")
                    suggestions["recommendations"].append("Implement GDPR-compliant consent collection (Article 7)")
                
                if "privacy policy" not in scenario_lower:
                    suggestions["issues"].append("No mention of privacy policy")
                    suggestions["recommendations"].append("Create and publish a GDPR-compliant privacy policy (Article 13)")
        
        elif reg_type == "ai_act":
            if any(term in scenario_lower for term in ["automated decision", "machine learning", "ai"]):
                if "high-risk" in scenario_lower or "loan" in scenario_lower or "hiring" in scenario_lower:
                    suggestions["issues"].append("Potential high-risk AI system requiring AI Act compliance")
                    suggestions["recommendations"].append("Conduct AI risk assessment and implement required safeguards")
                
                if "transparency" not in scenario_lower:
                    suggestions["issues"].append("AI transparency requirements may apply")
                    suggestions["recommendations"].append("Implement AI transparency measures and user notifications")
        
        elif reg_type == "dsa":
            if "platform" in scenario_lower or "content moderation" in scenario_lower:
                suggestions["issues"].append("Digital Services Act obligations may apply")
                suggestions["recommendations"].append("Implement DSA compliance measures for content moderation")
        
        elif reg_type == "consumer_rights":
            if "marketplace" in scenario_lower or "e-commerce" in scenario_lower:
                suggestions["issues"].append("Consumer rights obligations apply")
                suggestions["recommendations"].append("Ensure consumer rights compliance including withdrawal rights")
    
    return suggestions 