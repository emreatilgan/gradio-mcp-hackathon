#!/usr/bin/env python3
"""
EU AI Act Compliance Checker

This module provides tools for checking compliance with the EU AI Act regulation.
It includes risk assessment, compliance analysis, and recommendation generation
for AI systems and use cases.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime
import base64
import os

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

class ComplianceChecker:
    def __init__(self):
        self.processor = None
        self.is_initialized = False
        
        # LLM configuration
        self.llm_provider = None
        self.llm_client = None
        
        # PDF file management for Anthropic
        self.pdf_file_id = None
        self.pdf_path = "eu_ai_act.pdf"
        
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
        
        # If using Anthropic, try to upload PDF to their Files API
        if self.llm_provider == "anthropic":
            await self._upload_pdf_to_anthropic()
        
        self.is_initialized = True
        logging.info("Compliance checker initialized")
    
    async def _setup_llm(self):
        """Set up LLM connection based on available credentials"""
        
        # Try Anthropic first
        anthropic_api_key = self._get_env_var("ANTHROPIC_API_KEY")
        if anthropic_api_key and ANTHROPIC_AVAILABLE:
            self.llm_provider = "anthropic"
            self.llm_client = anthropic.Anthropic(api_key=anthropic_api_key)
            logging.info("Using Anthropic API for LLM")
            return
        
        # Try OpenAI as fallback
        openai_api_key = self._get_env_var("OPENAI_API_KEY")
        if openai_api_key and OPENAI_AVAILABLE:
            self.llm_provider = "openai"
            openai.api_key = openai_api_key
            self.llm_client = openai
            logging.info("Using OpenAI API for LLM")
            return
        
        # Require LLM API for testing
        raise ValueError("No LLM API key provided. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY for testing with original document.")
    
    async def _upload_pdf_to_anthropic(self):
        """Upload EU AI Act PDF to Anthropic's Files API"""
        if not os.path.exists(self.pdf_path):
            logging.warning(f"EU AI Act PDF not found at {self.pdf_path}. Will use semantic search fallback.")
            return
        
        try:
            # Check if we already have a file_id stored
            if os.path.exists("anthropic_file_id.txt"):
                with open("anthropic_file_id.txt", "r") as f:
                    stored_file_id = f.read().strip()
                
                # Verify the file still exists on Anthropic
                try:
                    file_info = self.llm_client.beta.files.retrieve_metadata(stored_file_id)
                    self.pdf_file_id = stored_file_id
                    logging.info(f"Using existing PDF file ID: {stored_file_id}")
                    return
                except Exception as e:
                    logging.info(f"Stored file ID invalid: {e}. Will upload new file.")
            
            # Upload new file
            logging.info("Uploading EU AI Act PDF to Anthropic Files API...")
            with open(self.pdf_path, "rb") as pdf_file:
                file_response = self.llm_client.beta.files.upload(
                    file=pdf_file
                )
            
            self.pdf_file_id = file_response.id
            
            # Store the file ID for future use
            with open("anthropic_file_id.txt", "w") as f:
                f.write(self.pdf_file_id)
            
            logging.info(f"Successfully uploaded PDF to Anthropic. File ID: {self.pdf_file_id}")
            
        except Exception as e:
            logging.error(f"Failed to upload PDF to Anthropic: {e}")
            logging.info("Will use semantic search fallback instead.")
    
    def _get_env_var(self, var_name: str) -> Optional[str]:
        """Get environment variable with fallback options"""
        return os.getenv(var_name)

    async def check_compliance(self, scenario: str) -> Dict:
        """Main function to check EU AI Act compliance for a scenario"""
        
        if not self.is_initialized:
            raise ValueError("Compliance checker not initialized. Call initialize() first.")
        
        if not scenario or not scenario.strip():
            return {
                "error": "Empty scenario provided",
                "scenario": scenario,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            logging.info(f"Starting compliance analysis for scenario")
            
            # 1. Analyze risk level
            risk_analysis = await self._analyze_risk_level(scenario)
            logging.info(f"Risk analysis completed: {risk_analysis.get('category', 'Unknown')}")
            
            # 2. Get relevant articles
            relevant_articles = await self._get_relevant_articles(scenario, risk_analysis.get("category", ""))
            logging.info(f"Found {len(relevant_articles)} relevant articles")
            
            # 3. Check compliance
            compliance_status = await self._check_compliance_status(scenario, risk_analysis.get("category", ""), relevant_articles)
            logging.info("Compliance status determined")

            recommendations = await self._generate_recommendations(scenario, risk_analysis, compliance_status)
            logging.info(f"Generated {len(recommendations)} recommendations")
            
            result = {
                "scenario": scenario,
                "compliance": compliance_status,
                "risk_level": risk_analysis,
                "articles": relevant_articles,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
                "analysis_method": "anthropic_pdf" if self.pdf_file_id and self.llm_provider == "anthropic" else "semantic_search"
            }
            
            logging.info("Compliance check completed successfully")
            return result
            
        except Exception as e:
            logging.error(f"Compliance check failed: {str(e)}")
            return {
                "error": f"Compliance analysis failed: {str(e)}",
                "scenario": scenario,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_risk_level(self, scenario: str) -> Dict:
        """Analyze and classify the risk level of the AI scenario"""
        
        logging.info("Analyzing risk level - preparing LLM prompt...")
        
        # Enhanced prompt for Anthropic with PDF support
        if self.llm_provider == "anthropic" and self.pdf_file_id:
            logging.info("Using Anthropic with PDF for risk analysis")
            prompt = f"""
            Based on the EU AI Act document provided, analyze the following AI use case scenario and classify it according to the official EU AI Act risk categories.

            Scenario: {scenario}

            Please refer to the official EU AI Act document to:
            1. Identify the specific risk category this scenario falls under
            2. Cite relevant articles and sections from the document
            3. Explain your reasoning based on the actual regulatory text

            EU AI Act Risk Categories (verify against document):
            1. UNACCEPTABLE RISK: Prohibited systems 
            2. HIGH RISK: Systems in critical areas requiring strict compliance
            3. LIMITED RISK: Systems requiring transparency obligations
            4. MINIMAL RISK: Low-risk systems with minimal obligations

            Provide your analysis in the following JSON format (ensure it's valid JSON without line breaks inside string values):
            {{
                "category": "High|Limited|Minimal|Unacceptable",
                "explanation": "Detailed explanation referencing specific EU AI Act articles and sections",
                "key_factors": ["factor1", "factor2", "factor3"],
                "cited_articles": ["Article X", "Article Y"],
                "regulatory_basis": "Direct quotes or references from the EU AI Act document - keep as single line"
            }}
            """
        else:
            # Fallback for semantic search or when PDF not available
            logging.info("Using rule-based analysis for risk classification")
            prompt = f"""
            Analyze the following AI scenario and classify it according to EU AI Act risk categories:

            Scenario: {scenario}

            Risk Categories:
            1. UNACCEPTABLE: Prohibited systems (social scoring, subliminal manipulation, real-time remote biometric identification in public spaces)
            2. HIGH: Critical infrastructure, biometric systems, employment, education, essential services, law enforcement
            3. LIMITED: Chatbots, emotion recognition, biometric categorization, AI-generated content
            4. MINIMAL: Video games, filters, simple recommendation systems

            Provide classification in JSON format (ensure valid JSON without line breaks inside strings):
            {{
                "category": "High|Limited|Minimal|Unacceptable",
                "explanation": "Detailed reasoning for classification",
                "key_factors": ["factor1", "factor2", "factor3"]
            }}
            """
        
        llm_response = await self._call_llm(prompt)
        
        logging.info("Parsing risk analysis JSON response...")
        try:
            # Clean the response to handle multiline JSON
            cleaned_response = self._clean_json_response(llm_response)
            risk_analysis = json.loads(cleaned_response)
            logging.info(f"Successfully parsed risk analysis JSON: {risk_analysis.get('category', 'Unknown')} risk")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse risk analysis LLM response as JSON: {e}")
            logging.error(f"Raw response: {llm_response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        return risk_analysis

    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response by removing problematic characters and fixing formatting"""
        import re
        
        # Remove any text before the first {
        start_idx = response.find('{')
        if start_idx > 0:
            response = response[start_idx:]
        
        # Remove any text after the last }
        end_idx = response.rfind('}')
        if end_idx >= 0:
            response = response[:end_idx + 1]
        
        # Replace problematic newlines within string values
        # This regex finds strings and replaces newlines within them
        def replace_newlines_in_strings(match):
            string_content = match.group(1)
            # Replace newlines with spaces within the string
            return '"' + string_content.replace('\n', ' ').replace('\r', ' ') + '"'
        
        # Apply the replacement to string values in JSON
        response = re.sub(r'"([^"]*(?:\n[^"]*)*)"', replace_newlines_in_strings, response)
        
        return response

    async def _get_relevant_articles(self, scenario: str, risk_category: str) -> List[Dict]:
        """Get relevant EU AI Act articles for the scenario"""
        
        # Use curated articles based on risk category instead of semantic search
        logging.info("Using curated articles based on risk category")
        return self._get_curated_articles(risk_category)

    def _get_curated_articles(self, risk_category: str) -> List[Dict]:
        """Get curated articles based on risk category"""
        
        if risk_category == "High":
            return [
                {"article_number": "6", "content": "High-risk AI systems classification"},
                {"article_number": "9-15", "content": "Requirements for high-risk AI systems"},
                {"article_number": "16", "content": "Quality management system"},
                {"article_number": "17", "content": "Documentation"},
                {"article_number": "19", "content": "Human oversight"}
            ]
        elif risk_category == "Limited":
            return [
                {"article_number": "50", "content": "Transparency obligations for certain AI systems"},
                {"article_number": "52", "content": "Information to be provided when AI systems interact with natural persons"}
            ]
        elif risk_category == "Unacceptable":
            return [
                {"article_number": "5", "content": "Prohibited AI practices"}
            ]
        else:  # Minimal
            return [
                {"article_number": "4", "content": "General principles and risk-based approach"}
            ]

    async def _check_compliance_status(self, scenario: str, risk_category: str, relevant_articles: List[Dict]) -> Dict:
        """Check compliance status against EU AI Act requirements"""
        
        # Enhanced compliance analysis for Anthropic with full PDF
        if self.llm_provider == "anthropic" and self.pdf_file_id:
            logging.info("Using Anthropic with PDF for compliance analysis")
            prompt = f"""
            Based on the complete EU AI Act document provided, determine if the following AI scenario complies with all applicable requirements.

            Scenario: {scenario}
            Risk Level: {risk_category}

            Please analyze the scenario against the full EU AI Act requirements by:
            1. Identifying all applicable articles and sections
            2. Checking compliance with specific requirements for {risk_category} risk systems
            3. Providing detailed reasoning based on the actual regulatory text
            4. Citing specific obligations that may or may not be met

            Provide analysis in JSON format:
            {{
                "compliant": true/false,
                "reasoning": "Detailed explanation referencing specific EU AI Act requirements",
                "applicable_articles": ["Article X", "Article Y"],
                "key_requirements": ["requirement1", "requirement2"],
                "potential_violations": ["violation1", "violation2"] // if any
            }}
            """
        else:
            logging.info("Using semantic search fallback for compliance analysis")
            # Fallback analysis using semantic search results
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
                "reasoning": "Detailed explanation of compliance status"
            }}
            """
        
        llm_response = await self._call_llm(prompt)
        
        logging.info("Parsing compliance analysis JSON response...")
        try:
            # Clean the response to handle multiline JSON
            cleaned_response = self._clean_json_response(llm_response)
            compliance_status = json.loads(cleaned_response)
            logging.info(f"Successfully parsed compliance JSON: {'COMPLIANT' if compliance_status.get('compliant') else 'NON-COMPLIANT'}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse compliance LLM response as JSON: {e}")
            logging.error(f"Raw response: {llm_response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        return compliance_status

    async def _determine_compliance(self, scenario: str, risk_analysis: Dict, relevant_articles: List[Dict]) -> Dict:
        """Determine compliance status (legacy method for backward compatibility)"""
        risk_category = risk_analysis.get("category", "Minimal")
        return await self._check_compliance_status(scenario, risk_category, relevant_articles)
    
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
        
        # Log the prompt being sent
        logging.info(f"=== LLM PROMPT ({self.llm_provider}) ===")
        logging.info(prompt)
        logging.info("=== END PROMPT ===")
        
        if self.llm_provider == "anthropic":
            response = await self._call_anthropic_api(prompt)
        elif self.llm_provider == "openai":
            response = await self._call_openai_api(prompt)
        else:
            raise ValueError("No LLM provider configured")
        
        # Log the LLM response
        logging.info(f"=== LLM RESPONSE ({self.llm_provider}) ===")
        logging.info(response)
        logging.info("=== END RESPONSE ===")
        
        return response
    
    async def _call_anthropic_api(self, prompt: str) -> str:
        """Call Anthropic API with PDF support"""
        
        try:
            # For now, use text-only approach since the file ID reference in messages 
            # doesn't seem to be supported in the current API version
            message_content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
            
            if self.pdf_file_id:
                logging.info(f"Note: PDF file uploaded (ID: {self.pdf_file_id}) but using text-only analysis due to API limitations")
            else:
                logging.info("Using Anthropic API without PDF")
            
            message = self.llm_client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Using latest Sonnet with PDF support
                max_tokens=2000,
                messages=[{"role": "user", "content": message_content}]
            )
            
            response_text = message.content[0].text
            logging.info(f"Anthropic API call successful, response length: {len(response_text)} characters")
            return response_text
            
        except Exception as e:
            logging.error(f"Anthropic API call failed: {str(e)}")
            raise
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            logging.info("Using OpenAI API")
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            logging.info(f"OpenAI API call successful, response length: {len(response_text)} characters")
            return response_text
            
        except Exception as e:
            logging.error(f"OpenAI API call failed: {str(e)}")
            raise 