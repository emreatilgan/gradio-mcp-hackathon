import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

# LLM integrations
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# For Nebius/other APIs
try:
    import requests
    import aiohttp
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

class ComplianceChecker:
    def __init__(self):
        self.processor = None
        self.is_initialized = False
        
        # LLM configuration
        self.llm_provider = None
        self.llm_client = None
        
        # EU AI Act risk categories
        self.risk_categories = {
            "Unacceptable": {
                "description": "Prohibited AI systems that pose unacceptable risks",
                "examples": ["Social scoring", "Subliminal manipulation", "Real-time biometric identification in public spaces"],
                "requirements": "Completely prohibited"
            },
            "High": {
                "description": "AI systems that pose high risks to safety and fundamental rights",
                "examples": ["Biometric systems", "Critical infrastructure", "Education/vocational training", "Employment", "Essential services", "Law enforcement", "Migration/asylum", "Administration of justice"],
                "requirements": "Strict requirements including conformity assessment, CE marking, risk management, data governance"
            },
            "Limited": {
                "description": "AI systems with specific transparency risks",
                "examples": ["Chatbots", "Emotion recognition", "Biometric categorization", "AI-generated content"],
                "requirements": "Transparency obligations - users must be informed they're interacting with AI"
            },
            "Minimal": {
                "description": "AI systems with minimal risk",
                "examples": ["AI-enabled video games", "AI filters", "Simple recommendation systems"],
                "requirements": "No specific obligations, but encouraged to follow voluntary codes of conduct"
            }
        }
    
    async def initialize(self, processor):
        """Initialize the compliance checker with document processor"""
        self.processor = processor
        await self._setup_llm()
        self.is_initialized = True
        logging.info("Compliance checker initialized")
    
    async def _setup_llm(self):
        """Set up LLM connection based on available credentials"""
        
        # Try Nebius first (from hackathon credits)
        nebius_api_key = self._get_env_var("NEBIUS_API_KEY")
        if nebius_api_key:
            self.llm_provider = "nebius"
            self.llm_client = self._create_nebius_client(nebius_api_key)
            logging.info("Using Nebius API for LLM")
            return
        
        # Try Anthropic
        anthropic_api_key = self._get_env_var("ANTHROPIC_API_KEY")
        if anthropic_api_key and ANTHROPIC_AVAILABLE:
            self.llm_provider = "anthropic"
            self.llm_client = anthropic.Anthropic(api_key=anthropic_api_key)
            logging.info("Using Anthropic API for LLM")
            return
        
        # Try OpenAI
        openai_api_key = self._get_env_var("OPENAI_API_KEY")
        if openai_api_key and OPENAI_AVAILABLE:
            self.llm_provider = "openai"
            openai.api_key = openai_api_key
            self.llm_client = openai
            logging.info("Using OpenAI API for LLM")
            return
        
        # Require LLM API for testing
        raise ValueError("No LLM API key provided. Please set NEBIUS_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY for testing with original document.")
    
    def _get_env_var(self, var_name: str) -> Optional[str]:
        """Get environment variable with common variations"""
        import os
        variations = [
            var_name,
            var_name.upper(),
            var_name.lower()
        ]
        
        for var in variations:
            value = os.getenv(var)
            if value:
                return value
        return None
    
    def _create_nebius_client(self, api_key: str):
        """Create Nebius API client"""
        return {
            "api_key": api_key,
            "base_url": "https://api.nebius.com/v1",  # Adjust based on actual Nebius endpoint
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        }
    
    async def check_compliance(self, scenario: str) -> Dict:
        """Main function to check EU AI Act compliance for a scenario"""
        if not self.is_initialized:
            raise ValueError("Compliance checker not initialized")
        
        try:
            # Step 1: Analyze scenario and classify risk level
            risk_analysis = await self._analyze_risk_level(scenario)
            
            # Step 2: Search for relevant articles
            relevant_articles = await self.processor.search_relevant_articles(scenario, top_k=5)
            
            # Step 3: Determine compliance status
            compliance_status = await self._determine_compliance(scenario, risk_analysis, relevant_articles)
            
            # Step 4: Generate recommendations
            recommendations = await self._generate_recommendations(scenario, risk_analysis, compliance_status)
            
            return {
                "scenario": scenario,
                "compliance": compliance_status,
                "risk_level": risk_analysis,
                "articles": relevant_articles,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Compliance check failed: {str(e)}")
            return {
                "error": f"Compliance analysis failed: {str(e)}",
                "scenario": scenario,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_risk_level(self, scenario: str) -> Dict:
        """Analyze and classify the risk level of the AI scenario"""
        
        # LLM-based analysis (no fallback for testing)
        prompt = f"""
        Analyze the following AI use case scenario and classify it according to EU AI Act risk categories:

        Scenario: {scenario}

        EU AI Act Risk Categories:
        1. UNACCEPTABLE RISK: Prohibited systems (social scoring, subliminal manipulation, real-time biometric ID in public)
        2. HIGH RISK: Systems in critical areas (biometrics, infrastructure, education, employment, essential services, law enforcement, migration, justice)
        3. LIMITED RISK: Systems requiring transparency (chatbots, emotion recognition, AI-generated content)
        4. MINIMAL RISK: Low-risk systems with no specific obligations

        Provide your analysis in the following JSON format:
        {{
            "category": "High|Limited|Minimal|Unacceptable",
            "confidence": 0.85,
            "explanation": "Detailed explanation of why this category was chosen",
            "key_factors": ["factor1", "factor2", "factor3"]
        }}
        """
        
        llm_response = await self._call_llm(prompt)
        
        # Parse JSON response
        risk_analysis = json.loads(llm_response)
        
        # Validate response
        if risk_analysis.get("category") not in ["High", "Limited", "Minimal", "Unacceptable"]:
            raise ValueError("Invalid risk category returned")
        
        return risk_analysis
    
    async def _determine_compliance(self, scenario: str, risk_analysis: Dict, relevant_articles: List[Dict]) -> Dict:
        """Determine compliance status based on risk level and scenario details"""
        
        risk_category = risk_analysis.get("category", "Minimal")
        
        # Unacceptable risk systems are always non-compliant
        if risk_category == "Unacceptable":
            return {
                "compliant": False,
                "confidence": 0.95,
                "reasoning": "This AI system is prohibited under EU AI Act Article 5 as it poses unacceptable risks."
            }
        
        # LLM-based compliance analysis (no fallback for testing)
        articles_text = "\n".join([f"Article {art.get('article_number', 'N/A')}: {art.get('content', '')[:500]}" 
                                  for art in relevant_articles[:3]])
        
        prompt = f"""
        Determine if the following AI scenario complies with EU AI Act requirements:

        Scenario: {scenario}
        Risk Level: {risk_category}
        
        Relevant EU AI Act Articles:
        {articles_text}

        Consider the requirements for {risk_category} risk AI systems:
        {self.risk_categories.get(risk_category, {}).get('requirements', 'Unknown')}

        Provide analysis in JSON format:
        {{
            "compliant": true/false,
            "confidence": 0.85,
            "reasoning": "Detailed explanation of compliance status"
        }}
        """
        
        llm_response = await self._call_llm(prompt)
        compliance_status = json.loads(llm_response)
        return compliance_status
    
    async def _generate_recommendations(self, scenario: str, risk_analysis: Dict, compliance_status: Dict) -> List[Dict]:
        """Generate compliance recommendations"""
        
        recommendations = []
        risk_category = risk_analysis.get("category", "Minimal")
        is_compliant = compliance_status.get("compliant", False)
        
        if risk_category == "Unacceptable":
            recommendations.append({
                "type": "Critical",
                "description": "This AI system is prohibited. Consider redesigning to eliminate prohibited practices or discontinue development."
            })
        
        elif risk_category == "High":
            if not is_compliant:
                recommendations.extend([
                    {
                        "type": "Legal Requirement",
                        "description": "Conduct conformity assessment with notified body before market placement"
                    },
                    {
                        "type": "Legal Requirement", 
                        "description": "Obtain CE marking and prepare EU declaration of conformity"
                    },
                    {
                        "type": "Technical",
                        "description": "Implement risk management system throughout AI system lifecycle"
                    },
                    {
                        "type": "Technical",
                        "description": "Establish data governance and quality management procedures"
                    },
                    {
                        "type": "Technical",
                        "description": "Ensure human oversight capabilities and transparency measures"
                    }
                ])
        
        elif risk_category == "Limited":
            if not is_compliant:
                recommendations.append({
                    "type": "Legal Requirement",
                    "description": "Inform users clearly and prominently that they are interacting with an AI system"
                })
        
        else:  # Minimal risk
            recommendations.append({
                "type": "Best Practice",
                "description": "Consider following voluntary AI ethics guidelines and codes of conduct"
            })
        
        # Add general recommendations
        recommendations.extend([
            {
                "type": "Documentation",
                "description": "Maintain comprehensive documentation of AI system design, training data, and decision logic"
            },
            {
                "type": "Monitoring",
                "description": "Implement post-market monitoring to track AI system performance and impacts"
            }
        ])
        
        return recommendations
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM with the prompt"""
        
        if self.llm_provider == "nebius":
            return await self._call_nebius_api(prompt)
        elif self.llm_provider == "anthropic":
            return await self._call_anthropic_api(prompt)
        elif self.llm_provider == "openai":
            return await self._call_openai_api(prompt)
        else:
            raise ValueError("No LLM provider configured")
    
    async def _call_nebius_api(self, prompt: str) -> str:
        """Call Nebius API"""
        if not HTTP_AVAILABLE:
            raise ValueError("HTTP client not available")
        
        # This is a placeholder - adjust based on actual Nebius API format
        payload = {
            "model": "llama-3.1-8b",  # Adjust model name
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.llm_client['base_url']}/chat/completions",
                headers=self.llm_client["headers"],
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"Nebius API error: {response.status}")
    
    async def _call_anthropic_api(self, prompt: str) -> str:
        """Call Anthropic API"""
        message = self.llm_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API"""
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content 