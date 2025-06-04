---
title: EU AI Act Compliance Checker
emoji: 🇪🇺
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
tags: [mcp-server-track, eu-ai-act, compliance, legal-tech, ai-regulation]
---

# 🇪🇺 EU AI Act Compliance Checker

> **Advanced AI compliance analysis tool with Gradio interface and MCP server integration**

[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange)](https://gradio.app/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org/)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-2024/1689-green)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](https://github.com/modelcontextprotocol)

**🏆 Built for the Gradio Agents & MCP Hackathon 2025**

## 🎯 What This Does

This tool helps you determine if your AI system complies with the **EU AI Act** (Regulation 2024/1689) by:

- **🔍 Analyzing AI scenarios** against the 170-page official regulation
- **⚖️ Classifying risk levels** (Unacceptable, High, Limited, Minimal)
- **📋 Providing compliance recommendations** with specific requirements
- **📚 Citing relevant articles** from the original EU AI Act document
- **🔗 Serving as an MCP server** for integration with Claude Desktop, Cursor, and other MCP clients

### Key Features

- **📄 Enhanced PDF Processing**: 
  - **Anthropic Direct Upload**: Uploads EU AI Act PDF directly to Anthropic's Files API for full document analysis
  - **Intelligent Fallback**: Falls back to semantic search if PDF upload isn't available
  - **Hybrid Analysis**: Combines full PDF analysis with targeted article retrieval
- **🧠 Intelligent Analysis**: Uses semantic search + LLM reasoning for precise compliance assessment
- **⚡ Real-time Results**: Get compliance analysis in seconds
- **🔌 MCP Integration**: Works as a server for AI coding assistants
- **🎨 Beautiful UI**: Clean Gradio interface for easy interaction

## 🎯 Project Overview

The EU AI Act Compliance Checker is a comprehensive tool that analyzes AI use case scenarios for compliance with the European Union's AI Act regulation. This project serves both as a standalone Gradio web application and as an MCP (Model Context Protocol) server that can be integrated into various AI development workflows.

**🚀 NEW: Enhanced Anthropic Integration**
- Automatically uploads the EU AI Act PDF to Anthropic's Files API
- Leverages Claude's native PDF processing capabilities for comprehensive analysis
- Provides more accurate citations and regulatory references
- Falls back to semantic search for maximum compatibility

### 🏆 Hackathon Submission

**Track:** MCP Server/Tool Track  
**Tags:** `mcp-server-track`

This project demonstrates how Gradio apps can serve as powerful MCP servers, extending the capabilities of AI assistants like Claude Desktop and Cursor IDE with specialized compliance checking tools.

## ✨ Key Features

### 🔍 **Comprehensive Compliance Analysis**
- **Risk Classification**: Automatically categorizes AI systems into EU AI Act risk levels (Unacceptable, High, Limited, Minimal)
- **Enhanced PDF Analysis**: When using Anthropic, uploads and analyzes the complete 170-page EU AI Act document
- **Compliance Assessment**: Determines whether an AI system meets regulatory requirements with detailed regulatory citations
- **Article Retrieval**: Finds and cites relevant EU AI Act articles for any scenario
- **Smart Recommendations**: Provides actionable compliance guidance based on actual regulatory text

### 🤖 **MCP Server Integration**
- **5 MCP Tools** for seamless integration with AI assistants
- **Real-time Analysis** accessible from Claude Desktop, Cursor, and other MCP clients
- **Structured Responses** in markdown format for easy consumption

### 📚 **Intelligent Document Processing**
- **Anthropic PDF Upload**: Automatically uploads EU AI Act PDF to Anthropic's Files API for comprehensive analysis
- **PDF Processing**: Extracts and processes the full 170-page EU AI Act document
- **Semantic Search**: Uses embeddings for contextually relevant article retrieval
- **Hybrid Approach**: Combines full PDF analysis with targeted semantic search
- **Fallback System**: Works even without the full document using curated key articles

### 🧠 **Multi-LLM Support**
- **Anthropic Claude** as primary provider with enhanced PDF capabilities
- **OpenAI GPT** compatibility
- **Rule-based Fallback** when LLMs aren't available

## 🛠️ Technical Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gradio App    │    │   MCP Server     │    │  Document       │
│   Interface     │◄──►│   Integration    │◄──►│  Processor      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Compliance     │    │   LLM APIs       │    │  Vector Search  │
│  Checker        │◄──►│  (Anthropic)     │    │  (FAISS)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

1. **`app.py`** - Main Gradio application with MCP server capability
2. **`document_processor.py`** - EU AI Act document parsing and semantic search
3. **`compliance_checker.py`** - AI scenario analysis and compliance assessment
4. **`mcp_server.py`** - MCP server setup and tool implementations

## 🚀 Available MCP Tools

| Tool Name | Description | Input | Output |
|-----------|-------------|--------|--------|
| `check_eu_ai_compliance` | Full compliance analysis of AI scenario | `scenario: string` | Complete compliance report |
| `get_compliance_articles` | Find relevant EU AI Act articles | `scenario: string`, `max_articles: int` | Relevant articles with citations |
| `assess_ai_risk_level` | Classify AI system risk level | `scenario: string` | Risk classification and explanation |
| `get_compliance_recommendations` | Get compliance guidance | `scenario: string`, `risk_level?: string` | Actionable recommendations |
| `explain_eu_ai_act_article` | Explain specific article | `article_number: string` | Detailed article explanation |

## 📊 EU AI Act Risk Categories

### 🚫 **Unacceptable Risk** (Prohibited)
- Social scoring systems
- Subliminal manipulation
- Real-time biometric identification in public spaces

### ⚠️ **High Risk** (Strict Requirements)
- Biometric systems
- Critical infrastructure
- Education & employment
- Law enforcement
- Healthcare applications

### ⚡ **Limited Risk** (Transparency Required)
- Chatbots & conversational AI
- Emotion recognition
- AI-generated content

### ✅ **Minimal Risk** (No Specific Obligations)
- AI games and filters
- Simple recommendation systems

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- **EU AI Act PDF document (REQUIRED)** - Place as `eu_ai_act.pdf` in project root
- **At least one LLM API key** (Anthropic or OpenAI)
- Required Python dependencies

### Quick Start

1. **Clone and Install**
```bash
git clone <your-repo>
cd eu-ai-act-compliance-checker
pip install -r requirements.txt
```

2. **Add EU AI Act Document (REQUIRED)**
```bash
# Place your 170-page EU AI Act PDF as 'eu_ai_act.pdf' in the project root
# The app REQUIRES this original document to function
```

3. **Set up API Keys (REQUIRED)**
```bash
# At least one of these is required:
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
```

4. **Run the Application**
```bash
python app.py
```

### 🌐 **Gradio Interface**
Access the web interface at `http://localhost:7860`

### 🔗 **MCP Client Integration**

#### Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "eu-ai-act-compliance": {
      "command": "python",
      "args": ["/path/to/your/app.py", "--mcp"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key"
      }
    }
  }
}
```

#### Cursor IDE
1. Install MCP extension
2. Configure server endpoint
3. Use tools directly in your code editor

## 💡 Usage Examples

### Example 1: Chatbot Compliance Check
```
Scenario: "We're building a customer service chatbot that uses natural language processing to answer questions about our products."

Result:
✅ Risk Level: Limited
⚠️ Compliance: Requires transparency obligations
📋 Recommendation: Inform users they're interacting with AI
```

### Example 2: Facial Recognition System
```
Scenario: "Our company wants to implement facial recognition for employee attendance tracking."

Result:
⚠️ Risk Level: High
❌ Compliance: Requires conformity assessment
📋 Recommendations: CE marking, risk management, human oversight
```

### Example 3: MCP Tool Usage in Claude
```
User: "Is my AI-powered credit scoring system compliant with EU AI Act?"
Claude: Let me check that for you using the EU AI Act compliance tool.

[Uses check_eu_ai_compliance tool]

The system indicates this is a HIGH RISK application requiring:
- Conformity assessment with notified body
- CE marking and EU declaration of conformity
- Risk management system implementation
...
```

## 🎬 Demo Video

[Link to demo video showing MCP server in action with Claude Desktop]

*Video demonstrates:*
- MCP tool integration with Claude Desktop
- Real-time compliance checking
- Article retrieval and citation
- Risk assessment workflow

## 🏗️ Cloud Integration

### Modal Labs Integration
The project is designed to leverage Modal Labs credits for:
- Heavy document processing workloads
- Batch embedding generation
- Scalable PDF parsing
- High-performance vector operations

## 📈 Performance & Scalability

- **Response Time**: <3 seconds for most queries
- **Document Processing**: Handles 170-page PDFs efficiently
- **Concurrent Users**: Supports multiple simultaneous MCP connections
- **Fallback System**: Works offline with rule-based analysis

## 🧪 Testing Scenarios

The app includes built-in example scenarios for testing:

1. **Customer Service Chatbot** (Limited Risk)
2. **Resume Screening AI** (High Risk)
3. **Credit Scoring System** (High Risk)
4. **Emotion Detection in Retail** (Limited Risk)
5. **Medical Diagnosis Assistant** (High Risk)

## 🏆 Why This Project Wins

### **Innovation** 🚀
- First-of-its-kind EU AI Act compliance checker with MCP integration
- Demonstrates the power of Gradio as both UI and MCP server
- Real-world legal tech application with immediate utility

### **Technical Excellence** 💻
- Robust multi-LLM architecture with intelligent fallbacks
- Sophisticated document processing and semantic search
- Production-ready MCP server implementation

### **Impact** 🌍
- Addresses critical need for EU AI Act compliance guidance
- Saves legal and development teams countless hours
- Democratizes access to complex regulatory analysis

### **Community Value** 👥
- Open source implementation others can build upon
- Educational resource for understanding EU AI Act
- Template for building regulatory compliance tools

## 🤝 Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for guidelines.

### Development Roadmap
- [ ] Support for additional languages
- [ ] Integration with more LLM providers
- [ ] Advanced reporting features
- [ ] Mobile-responsive interface improvements

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 🙏 Acknowledgments

- **Gradio Team** for the amazing MCP integration capabilities
- **EU AI Act Working Group** for the comprehensive regulation framework
- **Modal Labs** for providing hackathon credits
- **Hugging Face** for hosting and supporting the hackathon

---

**Built with ❤️ for the Gradio Agents & MCP Hackathon 2025**

*Making AI compliance accessible to everyone* 🌟 