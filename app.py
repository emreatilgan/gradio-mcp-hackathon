import gradio as gr
import json
import os
from typing import Dict, List, Optional, Tuple
import asyncio
from datetime import datetime

# Import MCP components
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP not available, running in standalone mode")

# Import our custom modules
from document_processor import EUAIActProcessor
from compliance_checker import ComplianceChecker
from mcp_server import setup_mcp_server

class EUAIActComplianceApp:
    def __init__(self):
        self.processor = EUAIActProcessor()
        self.checker = ComplianceChecker()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the document processor and compliance checker"""
        if not self.is_initialized:
            await self.processor.initialize()
            await self.checker.initialize(self.processor)
            self.is_initialized = True
    
    async def analyze_scenario(self, scenario: str) -> Dict:
        """Main function to analyze AI scenario for EU AI Act compliance"""
        if not self.is_initialized:
            try:
                await self.initialize()
            except Exception as e:
                return {
                    "error": f"Setup failed: {str(e)}. Please ensure you have:\n1. The original EU AI Act PDF as 'eu_ai_act.pdf'\n2. At least one LLM API key set (NEBIUS_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY)\n3. Required dependencies installed (pip install -r requirements.txt)",
                    "compliance": None,
                    "risk_level": None,
                    "articles": [],
                    "recommendations": []
                }
        
        if not scenario.strip():
            return {
                "error": "Please provide a scenario description",
                "compliance": None,
                "risk_level": None,
                "articles": [],
                "recommendations": []
            }
        
        try:
            # Get compliance analysis
            result = await self.checker.check_compliance(scenario)
            return result
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "compliance": None,
                "risk_level": None,
                "articles": [],
                "recommendations": []
            }

# Initialize the app
app = EUAIActComplianceApp()

def format_compliance_result(result: Dict) -> Tuple[str, str, str, str]:
    """Format the compliance result for Gradio interface"""
    
    if result.get("error"):
        return (
            f"❌ **Error:** {result['error']}", 
            "", 
            "", 
            ""
        )
    
    # Main compliance result
    compliance_status = result.get("compliance", {})
    is_compliant = compliance_status.get("compliant", False)
    confidence = compliance_status.get("confidence", 0)
    reasoning = compliance_status.get("reasoning", "")
    
    status_emoji = "✅" if is_compliant else "⚠️"
    compliance_html = f"""
    <div style="padding: 20px; border-radius: 10px; background-color: {'#d4edda' if is_compliant else '#fff3cd'};">
        <h3>{status_emoji} Compliance Status: {'COMPLIANT' if is_compliant else 'NON-COMPLIANT'}</h3>
        <p><strong>Confidence:</strong> {confidence:.1%}</p>
        <p><strong>Analysis:</strong> {reasoning}</p>
    </div>
    """
    
    # Risk level
    risk_level = result.get("risk_level", {})
    risk_category = risk_level.get("category", "Unknown")
    risk_explanation = risk_level.get("explanation", "")
    
    risk_colors = {
        "Minimal": "#d4edda",
        "Limited": "#fff3cd", 
        "High": "#f8d7da",
        "Unacceptable": "#f5c6cb"
    }
    
    risk_html = f"""
    <div style="padding: 15px; border-radius: 8px; background-color: {risk_colors.get(risk_category, '#f8f9fa')};">
        <h4>Risk Level: {risk_category}</h4>
        <p>{risk_explanation}</p>
    </div>
    """
    
    # Relevant articles
    articles = result.get("articles", [])
    articles_html = ""
    if articles:
        for article in articles[:5]:  # Show top 5 most relevant
            articles_html += f"""
            <div style="margin-bottom: 15px; padding: 10px; border-left: 3px solid #007bff; background-color: #f8f9fa;">
                <h5>Article {article.get('number', 'N/A')}: {article.get('title', 'Untitled')}</h5>
                <p><strong>Relevance:</strong> {article.get('relevance_score', 0):.1%}</p>
                <p>{article.get('excerpt', '')}</p>
            </div>
            """
    else:
        articles_html = "<p>No specific articles identified for this scenario.</p>"
    
    # Recommendations
    recommendations = result.get("recommendations", [])
    recommendations_html = ""
    if recommendations:
        recommendations_html = "<ul>"
        for rec in recommendations:
            recommendations_html += f"<li><strong>{rec.get('type', 'General')}:</strong> {rec.get('description', '')}</li>"
        recommendations_html += "</ul>"
    else:
        recommendations_html = "<p>No specific recommendations available.</p>"
    
    return compliance_html, risk_html, articles_html, recommendations_html

async def process_scenario(scenario: str):
    """Process the scenario and return formatted results"""
    result = await app.analyze_scenario(scenario)
    return format_compliance_result(result)

def sync_process_scenario(scenario: str):
    """Synchronous wrapper for Gradio"""
    return asyncio.run(process_scenario(scenario))

# Create Gradio interface
def create_interface():
    with gr.Blocks(
        title="EU AI Act Compliance Checker",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🇪🇺 EU AI Act Compliance Checker
        
        **Analyze your AI use case scenarios for compliance with the EU AI Act**
        
        **⚠️ REQUIREMENTS:**
        - Original EU AI Act PDF (`eu_ai_act.pdf`) in project root
        - LLM API key (Nebius, Anthropic, or OpenAI)
        
        This tool helps you understand:
        - Whether your AI system complies with EU AI Act requirements
        - Risk classification of your AI system
        - Relevant articles and regulations
        - Compliance recommendations
        
        ---
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                scenario_input = gr.Textbox(
                    label="🔍 Describe your AI use case scenario",
                    placeholder="Example: We are developing a facial recognition system for employee attendance tracking in our office building...",
                    lines=5
                )
                
                analyze_btn = gr.Button(
                    "🚀 Analyze Compliance", 
                    variant="primary",
                    size="lg"
                )
                
                gr.Examples(
                    examples=[
                        ["We are developing a chatbot for customer service that uses natural language processing to answer questions about our products."],
                        ["Our company wants to implement an AI system for automated resume screening to filter job applications."],
                        ["We are creating an AI-powered credit scoring system to evaluate loan applications for our bank."],
                        ["We plan to use AI for real-time emotion detection in our retail stores to understand customer satisfaction."],
                        ["Our medical startup is developing an AI system to assist doctors in diagnosing skin conditions from photos."]
                    ],
                    inputs=scenario_input,
                    label="📝 Example Scenarios"
                )
            
            with gr.Column(scale=1):
                gr.Markdown("""
                ### 🎯 MCP Integration
                
                This app also serves as an **MCP Server** that can be integrated into:
                - Claude Desktop
                - Cursor IDE  
                - Any MCP-compatible client
                
                **Available MCP Tools:**
                - `check_eu_ai_compliance`
                - `get_compliance_articles`
                - `assess_ai_risk_level`
                - `get_compliance_recommendations`
                """)
        
        gr.Markdown("---")
        
        # Results section
        with gr.Row():
            with gr.Column():
                compliance_result = gr.HTML(label="📊 Compliance Assessment")
                risk_result = gr.HTML(label="⚖️ Risk Classification")
        
        with gr.Row():
            with gr.Column():
                articles_result = gr.HTML(label="📚 Relevant EU AI Act Articles")
                recommendations_result = gr.HTML(label="💡 Compliance Recommendations")
        
        # Event handlers
        analyze_btn.click(
            fn=sync_process_scenario,
            inputs=[scenario_input],
            outputs=[compliance_result, risk_result, articles_result, recommendations_result]
        )
        
        scenario_input.submit(
            fn=sync_process_scenario,
            inputs=[scenario_input],
            outputs=[compliance_result, risk_result, articles_result, recommendations_result]
        )
        
        gr.Markdown("""
        ---
        ### 📖 About the EU AI Act
        
        The EU AI Act is the world's first comprehensive AI regulation, establishing rules for AI systems based on their risk levels:
        - **Unacceptable Risk**: Prohibited AI systems
        - **High Risk**: Strict requirements including conformity assessments
        - **Limited Risk**: Transparency obligations
        - **Minimal Risk**: No specific obligations
        
        This tool helps you navigate these requirements for your specific use case.
        """)
    
    return demo

# Create and configure the interface
demo = create_interface()

# Set up MCP server if available
if MCP_AVAILABLE:
    mcp_server = setup_mcp_server(app)

if __name__ == "__main__":
    # Initialize the app
    asyncio.run(app.initialize())
    
    # Launch the Gradio interface
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    ) 