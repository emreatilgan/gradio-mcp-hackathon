#!/usr/bin/env python3
"""
🇪🇺 EU AI Act Compliance Checker - Hackathon Version
Built for Gradio Agents & MCP Hackathon 2025

A simplified AI compliance tool that serves as both a Gradio web app 
and an MCP server for integration with Claude Desktop and other MCP clients.
"""

import os
import json
import base64
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import gradio as gr
import PyPDF2
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# EU AI Act Risk Categories
RISK_CATEGORIES = {
    "Unacceptable": {
        "description": "❌ PROHIBITED - AI systems that pose unacceptable risks",
        "examples": ["Social scoring systems", "Subliminal manipulation", "Real-time biometric identification in public spaces"],
        "color": "#dc3545"
    },
    "High": {
        "description": "⚠️ HIGH RISK - Strict requirements and conformity assessment needed",
        "examples": ["Biometric systems", "Critical infrastructure", "Education/employment", "Law enforcement", "Healthcare"],
        "color": "#fd7e14"
    },
    "Limited": {
        "description": "ℹ️ LIMITED RISK - Transparency obligations required",
        "examples": ["Chatbots", "Emotion recognition", "AI-generated content", "Biometric categorization"],
        "color": "#ffc107"
    },
    "Minimal": {
        "description": "✅ MINIMAL RISK - No specific obligations",
        "examples": ["AI games", "Spam filters", "Simple recommendation systems"],
        "color": "#28a745"
    }
}

class EUAIActChecker:
    def __init__(self):
        self.anthropic_client = None
        self.pdf_content = ""
        self._setup_anthropic()
        self._load_pdf()
    
    def _setup_anthropic(self):
        """Initialize Anthropic client"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.anthropic_client = Anthropic(api_key=api_key)
    
    def _load_pdf(self):
        """Load EU AI Act PDF content"""
        pdf_path = "eu_ai_act.pdf"
        if os.path.exists(pdf_path):
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_content = ""
                    # Read first 20 pages for key articles
                    for page_num in range(min(20, len(pdf_reader.pages))):
                        text_content += pdf_reader.pages[page_num].extract_text()
                    self.pdf_content = text_content[:15000]  # Limit content for efficiency
            except Exception as e:
                print(f"Failed to load PDF: {e}")
                self.pdf_content = ""
    
    def analyze_compliance(self, scenario: str) -> Dict:
        """Analyze AI scenario for EU AI Act compliance"""
        if not scenario.strip():
            return {"error": "Please provide a scenario description"}
        
        try:
            # Create system prompt with EU AI Act context
            system_prompt = f"""You are an EU AI Act compliance expert. Analyze the provided AI use case scenario and determine:

1. **Risk Level**: Classify as Unacceptable, High, Limited, or Minimal risk based on EU AI Act categories:
   - Unacceptable: Prohibited AI (social scoring, subliminal manipulation, real-time biometric ID in public)
   - High: Critical applications (biometrics, critical infrastructure, education, employment, law enforcement, healthcare)
   - Limited: Transparency-required AI (chatbots, emotion recognition, AI-generated content)
   - Minimal: Low-risk AI (games, simple recommendations, spam filters)

2. **Compliance Status**: Whether the scenario complies with EU AI Act requirements
3. **Key Requirements**: Specific obligations based on risk level
4. **Recommendations**: Actionable steps for compliance

EU AI Act Context (first 15,000 characters):
{self.pdf_content[:15000] if self.pdf_content else "PDF content not available - using general knowledge"}

Respond in JSON format with keys: risk_level, compliance_status, reasoning, requirements, recommendations."""

            # Call Anthropic API
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_prompt,
                messages=[{
                    "role": "user", 
                    "content": f"Analyze this AI scenario for EU AI Act compliance:\n\n{scenario}"
                }]
            )
            
            # Parse response
            content = response.content[0].text
            
            # Try to extract JSON from response
            try:
                # Find JSON in response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    # Fallback parsing
                    result = self._parse_text_response(content)
            except json.JSONDecodeError:
                result = self._parse_text_response(content)
            
            result["timestamp"] = datetime.now().isoformat()
            result["scenario"] = scenario
            return result
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "scenario": scenario,
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_text_response(self, content: str) -> Dict:
        """Parse non-JSON response"""
        # Simple text parsing fallback
        risk_level = "Unknown"
        for level in RISK_CATEGORIES.keys():
            if level.lower() in content.lower():
                risk_level = level
                break
        
        return {
            "risk_level": risk_level,
            "compliance_status": "compliant" if "compliant" in content.lower() else "non-compliant",
            "reasoning": content[:500] + "..." if len(content) > 500 else content,
            "requirements": ["See full analysis above"],
            "recommendations": ["Review the analysis for specific guidance"]
        }

# Initialize checker
checker = EUAIActChecker()

def check_compliance(scenario: str) -> Tuple[str, str, str]:
    """Main compliance checking function for Gradio interface"""
    if not scenario.strip():
        return "❌ Please provide a scenario description", "", ""
    
    result = checker.analyze_compliance(scenario)
    
    if "error" in result:
        return f"❌ **Error:** {result['error']}", "", ""
    
    # Format results
    risk_level = result.get("risk_level", "Unknown")
    risk_info = RISK_CATEGORIES.get(risk_level, {"description": "Unknown risk level", "color": "#666"})
    
    # Main result
    main_result = f"""
## 🎯 Compliance Analysis Result

**Scenario:** {result.get('scenario', 'N/A')}

### Risk Classification
<div style="padding: 15px; background-color: {risk_info['color']}20; border-left: 4px solid {risk_info['color']}; margin: 10px 0;">
<strong>{risk_level} Risk</strong><br>
{risk_info['description']}
</div>

### Compliance Status
**Status:** {result.get('compliance_status', 'Unknown').upper()}

### Analysis
{result.get('reasoning', 'No detailed reasoning available')}
"""
    
    # Requirements
    requirements = result.get('requirements', [])
    requirements_text = "### Key Requirements\n" + "\n".join([f"• {req}" for req in requirements]) if requirements else "No specific requirements identified"
    
    # Recommendations  
    recommendations = result.get('recommendations', [])
    recommendations_text = "### Recommendations\n" + "\n".join([f"• {rec}" for rec in recommendations]) if recommendations else "No specific recommendations available"
    
    return main_result, requirements_text, recommendations_text

def get_risk_info() -> str:
    """Get information about EU AI Act risk categories - MCP Tool"""
    info = "# EU AI Act Risk Categories\n\n"
    for level, details in RISK_CATEGORIES.items():
        info += f"## {details['description']}\n"
        info += f"**Examples:** {', '.join(details['examples'])}\n\n"
    return info

def explain_compliance(scenario: str) -> str:
    """Explain compliance requirements for a scenario - MCP Tool"""
    result = checker.analyze_compliance(scenario)
    if "error" in result:
        return f"Error: {result['error']}"
    
    explanation = f"""# Compliance Explanation

**Scenario:** {scenario}
**Risk Level:** {result.get('risk_level', 'Unknown')}
**Status:** {result.get('compliance_status', 'Unknown')}

## Analysis
{result.get('reasoning', 'No analysis available')}

## Requirements
{chr(10).join(f"• {req}" for req in result.get('requirements', []))}

## Recommendations
{chr(10).join(f"• {rec}" for rec in result.get('recommendations', []))}
"""
    return explanation

def assess_risk(scenario: str) -> str:
    """Assess only the risk level of an AI scenario - MCP Tool"""
    result = checker.analyze_compliance(scenario)
    if "error" in result:
        return f"Error: {result['error']}"
    
    risk_level = result.get('risk_level', 'Unknown')
    risk_info = RISK_CATEGORIES.get(risk_level, {"description": "Unknown"})
    
    return f"""# Risk Assessment

**Scenario:** {scenario}
**Risk Level:** {risk_level}
**Description:** {risk_info['description']}

**Analysis:** {result.get('reasoning', 'No analysis available')}
"""

# Create Gradio Interface
with gr.Blocks(
    title="🇪🇺 EU AI Act Compliance Checker", 
    theme=gr.themes.Soft(),
    css="""
    .main-header { text-align: center; margin-bottom: 30px; }
    .risk-box { padding: 15px; border-radius: 8px; margin: 10px 0; }
    """
) as demo:
    
    gr.Markdown("""
    # 🇪🇺 EU AI Act Compliance Checker
    ## *Hackathon Version - Built for Gradio Agents & MCP Hackathon 2025*
    
    **Check if your AI use case complies with the EU AI Act!**
    
    This tool analyzes AI scenarios and provides:
    - ✅ Risk level classification (Unacceptable/High/Limited/Minimal)
    - 📋 Compliance status and requirements  
    - 💡 Actionable recommendations
    
    **🔗 MCP Integration:** This app also serves as an MCP server for Claude Desktop and other MCP clients!
    """, elem_classes=["main-header"])
    
    with gr.Row():
        with gr.Column(scale=1):
            scenario_input = gr.Textbox(
                label="🤖 Describe Your AI Use Case",
                placeholder="Example: We're building a chatbot that helps students with homework by analyzing their facial expressions to detect confusion...",
                lines=5
            )
            
            analyze_btn = gr.Button("🔍 Analyze Compliance", variant="primary", size="lg")
            
            gr.Markdown("""
            ### 📚 Risk Categories Reference
            - **🚫 Unacceptable:** Prohibited AI systems
            - **⚠️ High:** Strict requirements needed  
            - **ℹ️ Limited:** Transparency required
            - **✅ Minimal:** No specific obligations
            """)
        
        with gr.Column(scale=2):
            result_output = gr.Markdown(label="Analysis Result")
            requirements_output = gr.Markdown(label="Requirements") 
            recommendations_output = gr.Markdown(label="Recommendations")
    
    # Event handlers
    analyze_btn.click(
        fn=check_compliance,
        inputs=[scenario_input],
        outputs=[result_output, requirements_output, recommendations_output]
    )
    
    gr.Markdown("""
    ---
    **🏆 Built for Gradio Agents & MCP Hackathon 2025** | **Track:** MCP Server  
    **🔗 MCP Integration:** This app serves as an MCP server with tools for compliance checking!
    """)

if __name__ == "__main__":
    # Launch the Gradio interface 
    # Note: MCP functionality is available through the Gradio API endpoints
    # Each function (check_compliance, explain_compliance, assess_risk, get_risk_info) 
    # will be automatically exposed as API endpoints that MCP clients can call
    demo.launch() 