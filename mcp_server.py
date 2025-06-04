import json
import logging
from typing import Dict, List, Any, Optional
import asyncio

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource, Tool, TextContent, ImageContent, EmbeddedResource,
        CallToolRequestParams, CallToolResult, ListResourcesResult,
        ListToolsResult, ReadResourceResult
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP server components not available")

def setup_mcp_server(app):
    """Set up MCP server with EU AI Act compliance tools"""
    
    if not MCP_AVAILABLE:
        logging.warning("MCP not available, server setup skipped")
        return None
    
    # Create MCP server
    server = Server("eu-ai-act-compliance")
    
    @server.list_tools()
    async def handle_list_tools() -> ListToolsResult:
        """List available MCP tools"""
        return ListToolsResult(
            tools=[
                Tool(
                    name="check_eu_ai_compliance",
                    description="Check if an AI use case scenario complies with EU AI Act requirements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scenario": {
                                "type": "string",
                                "description": "Description of the AI use case scenario to analyze"
                            }
                        },
                        "required": ["scenario"]
                    }
                ),
                Tool(
                    name="get_compliance_articles",
                    description="Get relevant EU AI Act articles for a specific AI scenario",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scenario": {
                                "type": "string", 
                                "description": "AI scenario to find relevant articles for"
                            },
                            "max_articles": {
                                "type": "integer",
                                "description": "Maximum number of articles to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["scenario"]
                    }
                ),
                Tool(
                    name="assess_ai_risk_level",
                    description="Assess the risk level of an AI system according to EU AI Act categories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scenario": {
                                "type": "string",
                                "description": "AI system description to assess risk level for"
                            }
                        },
                        "required": ["scenario"]
                    }
                ),
                Tool(
                    name="get_compliance_recommendations",
                    description="Get specific compliance recommendations for an AI system",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "scenario": {
                                "type": "string",
                                "description": "AI system scenario to get recommendations for"
                            },
                            "risk_level": {
                                "type": "string",
                                "description": "Known risk level (Optional: Minimal, Limited, High, Unacceptable)",
                                "enum": ["Minimal", "Limited", "High", "Unacceptable"]
                            }
                        },
                        "required": ["scenario"]
                    }
                ),
                Tool(
                    name="explain_eu_ai_act_article",
                    description="Get detailed explanation of a specific EU AI Act article",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "article_number": {
                                "type": "string",
                                "description": "Article number to explain (e.g., '5', '6', '52')"
                            }
                        },
                        "required": ["article_number"]
                    }
                )
            ]
        )
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle MCP tool calls"""
        
        try:
            if name == "check_eu_ai_compliance":
                return await _handle_compliance_check(app, arguments)
            
            elif name == "get_compliance_articles":
                return await _handle_get_articles(app, arguments)
            
            elif name == "assess_ai_risk_level":
                return await _handle_risk_assessment(app, arguments)
            
            elif name == "get_compliance_recommendations":
                return await _handle_get_recommendations(app, arguments)
            
            elif name == "explain_eu_ai_act_article":
                return await _handle_explain_article(app, arguments)
            
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )],
                    isError=True
                )
                
        except Exception as e:
            logging.error(f"Tool call failed: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"Tool execution failed: {str(e)}"
                )],
                isError=True
            )
    
    @server.list_resources()
    async def handle_list_resources() -> ListResourcesResult:
        """List available resources"""
        return ListResourcesResult(
            resources=[
                Resource(
                    uri="eu-ai-act://compliance-guide",
                    name="EU AI Act Compliance Guide",
                    description="Comprehensive guide to EU AI Act compliance requirements",
                    mimeType="text/markdown"
                ),
                Resource(
                    uri="eu-ai-act://risk-categories",
                    name="EU AI Act Risk Categories",
                    description="Explanation of EU AI Act risk classification system",
                    mimeType="application/json"
                )
            ]
        )
    
    @server.read_resource()
    async def handle_read_resource(uri: str) -> ReadResourceResult:
        """Handle resource reading"""
        
        if uri == "eu-ai-act://compliance-guide":
            guide_content = _generate_compliance_guide()
            return ReadResourceResult(
                contents=[TextContent(
                    type="text",
                    text=guide_content
                )]
            )
        
        elif uri == "eu-ai-act://risk-categories":
            risk_categories = _get_risk_categories_json()
            return ReadResourceResult(
                contents=[TextContent(
                    type="text",
                    text=json.dumps(risk_categories, indent=2)
                )]
            )
        
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    return server

async def _handle_compliance_check(app, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle full compliance check tool call"""
    scenario = arguments.get("scenario", "")
    
    if not scenario:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Error: Scenario description is required"
            )],
            isError=True
        )
    
    # Ensure app is initialized
    if not app.is_initialized:
        await app.initialize()
    
    # Run compliance analysis
    result = await app.analyze_scenario(scenario)
    
    if result.get("error"):
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Analysis failed: {result['error']}"
            )],
            isError=True
        )
    
    # Format result for MCP
    compliance = result.get("compliance", {})
    risk_level = result.get("risk_level", {})
    articles = result.get("articles", [])
    recommendations = result.get("recommendations", [])
    
    response_text = f"""# EU AI Act Compliance Analysis

## Scenario
{scenario}

## Compliance Status
**Status:** {"✅ COMPLIANT" if compliance.get("compliant") else "⚠️ NON-COMPLIANT"}
**Confidence:** {compliance.get("confidence", 0):.1%}
**Reasoning:** {compliance.get("reasoning", "No reasoning provided")}

## Risk Classification
**Risk Level:** {risk_level.get("category", "Unknown")}
**Confidence:** {risk_level.get("confidence", 0):.1%}
**Explanation:** {risk_level.get("explanation", "No explanation provided")}

## Relevant EU AI Act Articles
"""

    for i, article in enumerate(articles[:3], 1):
        response_text += f"""
### {i}. Article {article.get('article_number', 'N/A')}: {article.get('title', 'Untitled')}
**Relevance:** {article.get('relevance_score', 0):.1%}
{article.get('content', '')[:300]}...
"""

    response_text += "\n## Compliance Recommendations\n"
    for i, rec in enumerate(recommendations[:5], 1):
        response_text += f"{i}. **{rec.get('type', 'General')}:** {rec.get('description', '')}\n"
    
    return CallToolResult(
        content=[TextContent(
            type="text",
            text=response_text
        )]
    )

async def _handle_get_articles(app, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle get relevant articles tool call"""
    scenario = arguments.get("scenario", "")
    max_articles = arguments.get("max_articles", 5)
    
    if not scenario:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Error: Scenario description is required"
            )],
            isError=True
        )
    
    # Ensure app is initialized
    if not app.is_initialized:
        await app.initialize()
    
    # Search for relevant articles
    articles = await app.processor.search_relevant_articles(scenario, top_k=max_articles)
    
    if not articles:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="No relevant articles found for the given scenario."
            )]
        )
    
    response_text = f"# Relevant EU AI Act Articles for Scenario\n\n**Scenario:** {scenario}\n\n"
    
    for i, article in enumerate(articles, 1):
        response_text += f"""## {i}. Article {article.get('article_number', 'N/A')}: {article.get('title', 'Untitled')}
**Relevance Score:** {article.get('relevance_score', 0):.1%}

{article.get('content', '')}

---

"""
    
    return CallToolResult(
        content=[TextContent(
            type="text",
            text=response_text
        )]
    )

async def _handle_risk_assessment(app, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle risk level assessment tool call"""
    scenario = arguments.get("scenario", "")
    
    if not scenario:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Error: Scenario description is required"
            )],
            isError=True
        )
    
    # Ensure app is initialized
    if not app.is_initialized:
        await app.initialize()
    
    # Analyze risk level
    risk_analysis = await app.checker._analyze_risk_level(scenario)
    
    response_text = f"""# EU AI Act Risk Assessment

## Scenario
{scenario}

## Risk Classification
**Risk Level:** {risk_analysis.get("category", "Unknown")}
**Confidence:** {risk_analysis.get("confidence", 0):.1%}
**Explanation:** {risk_analysis.get("explanation", "No explanation provided")}

## Key Risk Factors
{', '.join(risk_analysis.get("key_factors", []))}

## Risk Category Requirements
"""
    
    risk_category = risk_analysis.get("category", "Minimal")
    if risk_category in app.checker.risk_categories:
        category_info = app.checker.risk_categories[risk_category]
        response_text += f"""
**Description:** {category_info.get("description", "")}
**Requirements:** {category_info.get("requirements", "")}
**Examples:** {', '.join(category_info.get("examples", []))}
"""
    
    return CallToolResult(
        content=[TextContent(
            type="text",
            text=response_text
        )]
    )

async def _handle_get_recommendations(app, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle get compliance recommendations tool call"""
    scenario = arguments.get("scenario", "")
    known_risk_level = arguments.get("risk_level")
    
    if not scenario:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Error: Scenario description is required"
            )],
            isError=True
        )
    
    # Ensure app is initialized
    if not app.is_initialized:
        await app.initialize()
    
    # If risk level is not provided, analyze it
    if not known_risk_level:
        risk_analysis = await app.checker._analyze_risk_level(scenario)
    else:
        risk_analysis = {"category": known_risk_level}
    
    # Mock compliance status for recommendations
    compliance_status = {"compliant": False}  # Assume non-compliant to get recommendations
    
    # Generate recommendations
    recommendations = await app.checker._generate_recommendations(scenario, risk_analysis, compliance_status)
    
    response_text = f"""# EU AI Act Compliance Recommendations

## Scenario
{scenario}

## Risk Level
{risk_analysis.get("category", "Unknown")}

## Compliance Recommendations

"""
    
    for i, rec in enumerate(recommendations, 1):
        response_text += f"### {i}. {rec.get('type', 'General')}\n{rec.get('description', '')}\n\n"
    
    return CallToolResult(
        content=[TextContent(
            type="text",
            text=response_text
        )]
    )

async def _handle_explain_article(app, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle explain specific article tool call"""
    article_number = arguments.get("article_number", "")
    
    if not article_number:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Error: Article number is required"
            )],
            isError=True
        )
    
    # Ensure app is initialized
    if not app.is_initialized:
        await app.initialize()
    
    # Get article information
    article = app.processor.get_article_by_number(article_number)
    
    if not article:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Article {article_number} not found in the EU AI Act database."
            )]
        )
    
    response_text = f"""# EU AI Act Article {article_number}

## Title
{article.get('title', 'Untitled')}

## Content
{article.get('content', 'No content available')}

## Article Number
{article.get('number', article_number)}
"""
    
    return CallToolResult(
        content=[TextContent(
            type="text", 
            text=response_text
        )]
    )

def _generate_compliance_guide() -> str:
    """Generate compliance guide content"""
    return """# EU AI Act Compliance Guide

## Overview
The EU AI Act is the world's first comprehensive AI regulation, establishing a risk-based approach to AI governance.

## Risk Categories

### 1. Unacceptable Risk (Prohibited)
- Social scoring systems
- Subliminal manipulation techniques
- Real-time biometric identification in public spaces (with exceptions)

### 2. High Risk
Systems in critical areas requiring strict compliance:
- Biometric identification and categorization
- Critical infrastructure management
- Education and vocational training
- Employment, workers management and access to self-employment
- Access to and enjoyment of essential private services and public services
- Law enforcement
- Migration, asylum and border control management
- Administration of justice and democratic processes

**Requirements:**
- Conformity assessment
- CE marking
- Risk management system
- Data governance and quality
- Transparency and human oversight
- Accuracy and robustness

### 3. Limited Risk  
Systems requiring transparency:
- Chatbots and conversational AI
- Emotion recognition systems
- Biometric categorization systems
- AI-generated content

**Requirements:**
- Clear information to users that they are interacting with AI

### 4. Minimal Risk
No specific legal obligations, but encouraged to follow voluntary codes of conduct.

## Compliance Steps

1. **Classify your AI system** according to risk categories
2. **Implement required measures** based on classification
3. **Document compliance** with technical documentation
4. **Conduct assessments** as required
5. **Monitor and maintain** compliance post-deployment

## Key Deadlines
- August 2024: Prohibited practices ban
- February 2025: General purpose AI model requirements
- August 2026: Full regulation in effect
"""

def _get_risk_categories_json() -> Dict:
    """Get risk categories as JSON structure"""
    return {
        "eu_ai_act_risk_categories": {
            "Unacceptable": {
                "description": "Prohibited AI systems that pose unacceptable risks",
                "examples": ["Social scoring", "Subliminal manipulation", "Real-time biometric identification in public spaces"],
                "requirements": "Completely prohibited",
                "legal_basis": "Article 5"
            },
            "High": {
                "description": "AI systems that pose high risks to safety and fundamental rights", 
                "examples": ["Biometric systems", "Critical infrastructure", "Education", "Employment", "Essential services", "Law enforcement", "Migration", "Administration of justice"],
                "requirements": "Strict requirements including conformity assessment, CE marking, risk management, data governance",
                "legal_basis": "Articles 6-51"
            },
            "Limited": {
                "description": "AI systems with specific transparency risks",
                "examples": ["Chatbots", "Emotion recognition", "Biometric categorization", "AI-generated content"],
                "requirements": "Transparency obligations - users must be informed they're interacting with AI",
                "legal_basis": "Article 52"
            },
            "Minimal": {
                "description": "AI systems with minimal risk",
                "examples": ["AI-enabled video games", "AI filters", "Simple recommendation systems"],
                "requirements": "No specific obligations, but encouraged to follow voluntary codes of conduct",
                "legal_basis": "General provisions"
            }
        }
    } 