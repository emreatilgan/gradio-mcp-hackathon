#!/usr/bin/env python3
"""
EU Regulations Compliance Checker - MCP Server
A Gradio app that functions as an MCP server for checking EU regulatory compliance.

Track: MCP Tool/Server - Building Gradio apps that function as MCP servers
Uses CELLAR SPARQL endpoint for official EU legal data with fallback knowledge base.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
import requests
from urllib.parse import quote
import gradio as gr
from datetime import datetime
import re

# Import fallback knowledge base
from eu_regulations_knowledge import (
    detect_regulation_types, 
    get_compliance_suggestions, 
    search_regulations_by_keywords,
    get_regulation_info
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EURegulationsQuerier:
    """Query EU regulations using CELLAR SPARQL endpoint with fallback"""
    
    def __init__(self):
        self.endpoint = "https://publications.europa.eu/webapi/rdf/sparql"
        self.use_fallback = False
        self.prefixes = """
        prefix cdm: <http://publications.europa.eu/ontology/cdm#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix dcterms: <http://purl.org/dc/terms/>
        prefix skos: <http://www.w3.org/2004/02/skos/core#>
        prefix owl: <http://www.w3.org/2002/07/owl#>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        prefix purl: <http://purl.org/dc/elements/1.1/>
        """
    
    def execute_sparql(self, query: str) -> List[Dict]:
        """Execute SPARQL query against CELLAR endpoint"""
        if self.use_fallback:
            return []
            
        try:
            params = {
                'query': query,
                'format': 'json',
                'timeout': 30000
            }
            
            response = requests.get(self.endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'results' in data and 'bindings' in data['results']:
                for binding in data['results']['bindings']:
                    result = {}
                    for key, value in binding.items():
                        result[key] = value.get('value', '')
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.warning(f"SPARQL query failed, switching to fallback: {e}")
            self.use_fallback = True
            return []
    
    def find_relevant_regulations_sparql(self, keywords: str, regulation_type: str = "") -> List[Dict]:
        """Find EU regulations using SPARQL (primary method)"""
        
        # Construct filter based on regulation type
        type_filter = ""
        if regulation_type.lower() == "gdpr":
            type_filter = 'FILTER(CONTAINS(LCASE(?title), "data protection") || CONTAINS(LCASE(?title), "gdpr"))'
        elif regulation_type.lower() == "ai_act":
            type_filter = 'FILTER(CONTAINS(LCASE(?title), "artificial intelligence"))'
        elif regulation_type.lower() == "dsa":
            type_filter = 'FILTER(CONTAINS(LCASE(?title), "digital services"))'
        else:
            # General keyword search
            keyword_terms = [k.strip().lower() for k in keywords.split() if len(k.strip()) > 2]
            if keyword_terms:
                conditions = " || ".join([f'CONTAINS(LCASE(?title), "{term}")' for term in keyword_terms])
                type_filter = f'FILTER({conditions})'
        
        query = f"""
        {self.prefixes}
        SELECT DISTINCT ?work ?title ?celex ?date ?type WHERE {{
            ?work rdf:type ?type ;
                  rdfs:label ?title ;
                  dcterms:issued ?date .
            OPTIONAL {{ ?work owl:sameAs ?celex }}
            FILTER(?type = cdm:legal-act || ?type = cdm:directive || ?type = cdm:regulation)
            {type_filter}
        }} ORDER BY DESC(?date) LIMIT 10
        """
        
        return self.execute_sparql(query)
    
    def find_relevant_regulations_fallback(self, keywords: str, regulation_type: str = "") -> List[Dict]:
        """Find EU regulations using fallback knowledge base"""
        if regulation_type:
            # Get specific regulation info
            reg_info = get_regulation_info(regulation_type)
            if reg_info:
                return [{
                    "title": reg_info["title"],
                    "celex": reg_info["celex"], 
                    "date": reg_info["date"],
                    "url": reg_info["url"]
                }]
        
        # Search by keywords
        keyword_list = keywords.split() if keywords else []
        return search_regulations_by_keywords(keyword_list)
    
    def find_relevant_regulations(self, keywords: str, regulation_type: str = "") -> List[Dict]:
        """Find EU regulations with SPARQL primary, fallback secondary"""
        
        # Try SPARQL first
        if not self.use_fallback:
            results = self.find_relevant_regulations_sparql(keywords, regulation_type)
            if results:
                return results
        
        # Use fallback
        return self.find_relevant_regulations_fallback(keywords, regulation_type)

class ComplianceAnalyzer:
    """Analyze compliance scenarios using enhanced AI reasoning"""
    
    def __init__(self):
        self.querier = EURegulationsQuerier()
    
    def extract_keywords(self, scenario: str) -> List[str]:
        """Extract relevant keywords from scenario text using fallback system"""
        # Use enhanced detection from knowledge base
        detected_types = detect_regulation_types(scenario)
        
        # Extract general keywords
        words = re.findall(r'\b\w+\b', scenario.lower())
        relevant_words = [w for w in words if len(w) > 3]
        
        return relevant_words, detected_types
    
    def analyze_compliance(self, scenario: str) -> Dict[str, Any]:
        """Main compliance analysis function with enhanced fallback support"""
        
        # Extract keywords and detect regulation types
        keywords, detected_regulations = self.extract_keywords(scenario)
        
        # Get compliance suggestions from knowledge base
        compliance_suggestions = get_compliance_suggestions(detected_regulations, scenario)
        
        # Query relevant regulations
        all_regulations = []
        for reg_type in detected_regulations:
            regs = self.querier.find_relevant_regulations("", reg_type)
            all_regulations.extend(regs)
        
        # If no specific regulations detected, do general search
        if not all_regulations and keywords:
            general_keywords = " ".join(keywords[:5])  # Use first 5 keywords
            all_regulations = self.querier.find_relevant_regulations(general_keywords)
        
        # Enhanced compliance analysis using knowledge base
        compliance_result = self._enhanced_compliance_check(scenario, detected_regulations, compliance_suggestions)
        
        return {
            "scenario": scenario,
            "detected_regulations": detected_regulations,
            "relevant_regulations": all_regulations,
            "compliance_status": compliance_result["status"],
            "compliance_details": compliance_result["details"],
            "recommendations": compliance_result["recommendations"],
            "confidence": compliance_result["confidence"],
            "data_source": "Fallback Knowledge Base" if self.querier.use_fallback else "SPARQL + Knowledge Base",
            "timestamp": datetime.now().isoformat()
        }
    
    def _enhanced_compliance_check(self, scenario: str, regulation_types: List[str], suggestions: Dict) -> Dict[str, Any]:
        """Enhanced compliance checking using knowledge base suggestions"""
        
        issues = suggestions.get("issues", [])
        recommendations = suggestions.get("recommendations", [])
        
        # Add general compliance insights
        scenario_lower = scenario.lower()
        
        # Additional checks
        if not issues:
            issues.append("No major compliance issues detected based on scenario description")
        
        if not recommendations:
            recommendations.append("Continue monitoring for regulatory changes and ensure regular compliance reviews")
        
        # Enhanced confidence scoring
        confidence = 0.9 if suggestions.get("regulations") else 0.7
        
        # Determine overall compliance status
        if len(issues) <= 1 and "no major" in str(issues).lower():
            status = "LIKELY_COMPLIANT"
            confidence = min(confidence, 0.85)
        elif len(issues) <= 3:
            status = "REQUIRES_REVIEW"
            confidence = min(confidence, 0.7)
        else:
            status = "NON_COMPLIANT"
            confidence = min(confidence, 0.9)
        
        return {
            "status": status,
            "details": issues,
            "recommendations": recommendations,
            "confidence": confidence
        }

# Initialize the analyzer
analyzer = ComplianceAnalyzer()

def check_compliance(scenario_text: str) -> str:
    """Main compliance checking function for Gradio interface"""
    
    if not scenario_text.strip():
        return "Please provide a scenario description to analyze."
    
    try:
        # Perform compliance analysis
        result = analyzer.analyze_compliance(scenario_text)
        
        # Format results for display
        output = f"""
# 🇪🇺 EU Regulations Compliance Analysis

## 📋 Scenario Analyzed
{result['scenario']}

## 🔍 Detected Regulation Areas
{', '.join(result['detected_regulations']) if result['detected_regulations'] else 'General compliance check'}

## ⚖️ Compliance Status: **{result['compliance_status']}**
**Confidence Level:** {result['confidence']:.0%}  
**Data Source:** {result['data_source']}

## 📊 Analysis Details
"""
        
        for detail in result['compliance_details']:
            output += f"• {detail}\n"
        
        output += "\n## 💡 Recommendations\n"
        for rec in result['recommendations']:
            output += f"• {rec}\n"
        
        if result['relevant_regulations']:
            output += "\n## 📜 Relevant EU Regulations Found\n"
            for reg in result['relevant_regulations'][:3]:  # Show top 3
                title = reg.get('title', 'Unknown Title')
                date = reg.get('date', 'Unknown Date')
                celex = reg.get('celex', '')
                url = reg.get('url', '')
                
                output += f"**{title}**\n"
                output += f"Date: {date}\n"
                if celex:
                    output += f"CELEX: {celex}\n"
                if url:
                    output += f"Official Link: [View Regulation]({url})\n"
                output += "\n"
        
        output += f"\n---\n*Analysis completed at {result['timestamp']}*"
        
        return output
        
    except Exception as e:
        logger.error(f"Compliance check failed: {e}")
        return f"Error analyzing compliance: {str(e)}"

def test_sparql_connection() -> str:
    """Test function to verify SPARQL endpoint connectivity"""
    
    try:
        querier = EURegulationsQuerier()
        
        # Simple test query
        test_query = f"""
        {querier.prefixes}
        SELECT ?work ?title WHERE {{
            ?work rdf:type cdm:legal-act ;
                  rdfs:label ?title .
            FILTER(CONTAINS(LCASE(?title), "data protection"))
        }} LIMIT 3
        """
        
        results = querier.execute_sparql(test_query)
        
        if results:
            output = "✅ **SPARQL Connection Successful!**\n\n"
            output += "Sample EU regulations found:\n\n"
            for result in results:
                output += f"• {result.get('title', 'Unknown')}\n"
            return output
        else:
            output = "⚠️ **SPARQL Not Available - Using Fallback Knowledge Base**\n\n"
            output += "Testing fallback system with GDPR information:\n\n"
            
            # Test fallback system
            gdpr_info = get_regulation_info("gdpr")
            if gdpr_info:
                output += f"✅ {gdpr_info['title']}\n"
                output += f"✅ CELEX: {gdpr_info['celex']}\n"
                output += f"✅ Date: {gdpr_info['date']}\n"
                output += "\n**Fallback system operational!**"
            
            return output
            
    except Exception as e:
        return f"❌ System error: {str(e)}"

# Create Gradio interface
with gr.Blocks(
    title="EU Regulations Compliance Checker",
    theme=gr.themes.Soft(),
    css="""
    .main-header { text-align: center; margin-bottom: 2rem; }
    .feature-box { padding: 1rem; border: 1px solid #ddd; border-radius: 8px; margin: 1rem 0; }
    .status-box { padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .compliant { background-color: #d4edda; border: 1px solid #c3e6cb; }
    .review { background-color: #fff3cd; border: 1px solid #ffeaa7; }
    .non-compliant { background-color: #f8d7da; border: 1px solid #f5c6cb; }
    """
) as demo:
    
    gr.HTML("""
    <div class="main-header">
        <h1>🇪🇺 EU Regulations Compliance Checker</h1>
        <p><strong>MCP Server for EU Legal Compliance Analysis</strong></p>
        <p>Powered by EU legal database with intelligent fallback system</p>
        <p><em>Gradio Agents & MCP Hackathon 2025 • Track: MCP Tool/Server</em></p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.HTML("""
            <div class="feature-box">
                <h3>📋 How to Use</h3>
                <ol>
                    <li>Describe your business scenario or use case</li>
                    <li>Include relevant details about data processing, AI systems, or digital services</li>
                    <li>Get compliance analysis with specific EU regulations</li>
                    <li>Receive actionable recommendations</li>
                </ol>
                <p><strong>Supported Regulations:</strong> GDPR, AI Act, DSA, Consumer Rights, eIDAS</p>
            </div>
            """)
            
            scenario_input = gr.Textbox(
                label="Describe your scenario for compliance checking",
                placeholder="Example: We process user personal data for personalized recommendations using machine learning algorithms...",
                lines=6,
                value=""
            )
            
            with gr.Row():
                check_btn = gr.Button("🔍 Check Compliance", variant="primary", size="lg")
                test_btn = gr.Button("🔗 Test System Status", variant="secondary")
        
        with gr.Column(scale=3):
            output_display = gr.Markdown(
                label="Compliance Analysis Results",
                value="Enter a scenario and click '🔍 Check Compliance' to begin analysis."
            )
    
    # Quick Test Scenarios
    with gr.Row():
        gr.HTML("""
        <div class="feature-box">
            <h3>💡 Quick Test Scenarios</h3>
        </div>
        """)
    
    with gr.Row():
        with gr.Column():
            gdpr_btn = gr.Button("📊 GDPR: E-commerce Data", size="sm")
            ai_btn = gr.Button("🤖 AI Act: Loan Approval", size="sm")
        with gr.Column():
            dsa_btn = gr.Button("📱 DSA: Social Platform", size="sm")
            consumer_btn = gr.Button("🛒 Consumer: Marketplace", size="sm")
    
    # Predefined scenarios
    gdpr_scenario = "Our e-commerce platform collects customer email addresses, purchase history, and browsing behavior to provide personalized product recommendations and send marketing emails."
    ai_scenario = "We use machine learning algorithms to automatically approve or reject loan applications based on customer financial data, credit scores, and behavioral patterns."
    dsa_scenario = "Our social media platform allows users to upload content and we use automated content moderation systems to detect and remove harmful content."
    consumer_scenario = "We operate an online marketplace where third-party sellers offer products to consumers. We handle payments and customer service."
    
    # Event handlers
    check_btn.click(
        fn=check_compliance,
        inputs=[scenario_input],
        outputs=[output_display]
    )
    
    test_btn.click(
        fn=test_sparql_connection,
        inputs=[],
        outputs=[output_display]
    )
    
    # Quick scenario buttons
    gdpr_btn.click(lambda: gdpr_scenario, outputs=[scenario_input])
    ai_btn.click(lambda: ai_scenario, outputs=[scenario_input])
    dsa_btn.click(lambda: dsa_scenario, outputs=[scenario_input])
    consumer_btn.click(lambda: consumer_scenario, outputs=[scenario_input])
    
    # MCP Server Information
    gr.HTML("""
    <div class="feature-box">
        <h3>🔧 MCP Server Information</h3>
        <p><strong>Server Type:</strong> EU Regulations Compliance Checker</p>
        <p><strong>Primary Data Source:</strong> EU CELLAR SPARQL Database</p>
        <p><strong>Fallback System:</strong> Curated EU Regulations Knowledge Base</p>
        <p><strong>Supported Regulations:</strong> GDPR, AI Act, DSA, Consumer Protection, eIDAS</p>
        <p><strong>Hackathon Track:</strong> MCP Tool/Server - Building Gradio apps that function as MCP servers</p>
        <p><strong>Integration:</strong> Compatible with Claude Desktop, Cursor, and other MCP clients</p>
    </div>
    """)

if __name__ == "__main__":
    # Launch as MCP server
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True,
        debug=True
    ) 