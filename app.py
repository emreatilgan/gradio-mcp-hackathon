import gradio as gr
import json
import os
import logging
from typing import Dict, List, Optional, Tuple
import asyncio
from datetime import datetime

# Configure logging to show detailed information including LLM interactions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('compliance_checker.log')  # Also log to file
    ]
)

# Set up logger for this module
logger = logging.getLogger(__name__)
logger.info("EU AI Act Compliance Checker starting up...")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ Environment variables loaded from .env file")
except ImportError:
    logger.warning("⚠️  python-dotenv not available, using system environment variables only")

# Import MCP components
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
    logger.info("MCP components loaded successfully")
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP not available, running in standalone mode")

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
                    "error": f"Setup failed: {str(e)}. Please ensure you have:\n1. The original EU AI Act PDF as 'eu_ai_act.pdf'\n2. At least one LLM API key set (ANTHROPIC_API_KEY or OPENAI_API_KEY)\n3. Required dependencies installed (pip install -r requirements.txt)",
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

def format_compliance_result(result: Dict) -> Tuple[str, str, str]:
    """Format the compliance result for Gradio interface"""
    
    if result.get("error"):
        return (
            f"❌ **Error:** {result['error']}", 
            "", 
            ""
        )
    
    # Analysis method indicator
    analysis_method = result.get("analysis_method", "semantic_search")
    method_badge = "🤖 **Enhanced PDF Analysis**" if analysis_method == "anthropic_pdf" else "🔍 **Semantic Search Analysis**"
    
    # Main compliance result
    compliance_status = result.get("compliance", {})
    is_compliant = compliance_status.get("compliant", False)
    reasoning = compliance_status.get("reasoning", "")
    
    status_emoji = "✅" if is_compliant else "⚠️"
    compliance_html = f"""
    <div style="padding: 20px; border-radius: 10px; background-color: {'#d4edda' if is_compliant else '#fff3cd'};">
        <div style="margin-bottom: 10px;">{method_badge}</div>
        <h3>{status_emoji} Compliance Status: {'COMPLIANT' if is_compliant else 'NON-COMPLIANT'}</h3>
        <p><strong>Analysis:</strong> {reasoning}</p>
    </div>
    """
    
    # Risk level
    risk_level = result.get("risk_level", {})
    risk_category = risk_level.get("category", "Unknown")
    risk_explanation = risk_level.get("explanation", "")
    
    # Enhanced details for PDF analysis
    cited_articles = risk_level.get("cited_articles", [])
    regulatory_basis = risk_level.get("regulatory_basis", "")
    
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
        {f'<p><strong>Cited Articles:</strong> {", ".join(cited_articles)}</p>' if cited_articles else ''}
        {f'<p><strong>Regulatory Basis:</strong> {regulatory_basis}</p>' if regulatory_basis else ''}
    </div>
    """
    
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
    
    return compliance_html, risk_html, recommendations_html

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
            max-width: 1400px !important;
        }
        .results-column {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🇪🇺 EU AI Act Compliance Checker
        
        **Analyze your AI use case scenarios for compliance with the EU AI Act**
        
        This tool helps you understand:
        - Whether your scenario complies with EU AI Act requirements
        - Risk classification of your scenario
        - Relevant articles and regulations
        - Compliance recommendations
        """)
        
        # MCP Integration section at the top
        gr.Markdown("""
        ---
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
        
        ---
        """)
        
        # Main content area: Input on left, Results on right
        with gr.Row():
            # Input section
            with gr.Column(scale=1):
                scenario_input = gr.Textbox(
                    label="🔍 Describe your AI use case scenario",
                    placeholder="Example: We are developing a facial recognition system for employee attendance tracking in our office building...",
                    lines=8
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
            
            # Results section on the right
            with gr.Column(scale=1, elem_classes=["results-column"]):
                gr.Markdown("### 📊 Analysis Results")
                compliance_result = gr.HTML(label="Compliance Assessment")
                risk_result = gr.HTML(label="⚖️ Risk Classification")
                recommendations_result = gr.HTML(label="💡 Compliance Recommendations")
        
        # Event handlers
        analyze_btn.click(
            fn=sync_process_scenario,
            inputs=[scenario_input],
            outputs=[compliance_result, risk_result, recommendations_result]
        )
        
        scenario_input.submit(
            fn=sync_process_scenario,
            inputs=[scenario_input],
            outputs=[compliance_result, risk_result, recommendations_result]
        )
    
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