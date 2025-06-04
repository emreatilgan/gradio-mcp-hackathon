# 🇪🇺 EU AI Act Compliance Checker - Hackathon Version

> **🏆 Built for Gradio Agents & MCP Hackathon 2025**  
> **Track:** MCP Server/Tool Track  
> **Tags:** `mcp-server-track`

[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange)](https://gradio.app/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org/)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-2024/1689-green)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](https://github.com/modelcontextprotocol)

## 🎯 What This Does

A **simplified AI compliance tool** that helps determine if your AI system complies with the **EU AI Act** by:

- 🔍 **Analyzing AI scenarios** against EU AI Act requirements
- ⚖️ **Classifying risk levels** (Unacceptable, High, Limited, Minimal)  
- 📋 **Providing compliance guidance** with specific recommendations
- 🔗 **Serving as an MCP server** for integration with Claude Desktop, Cursor, and other MCP clients

## ✨ Key Features

### 🤖 **Intelligent Analysis**
- **Anthropic Claude Integration**: Uses Claude-3.5-Sonnet for precise compliance assessment
- **EU AI Act Knowledge**: Incorporates actual regulation text for accurate analysis
- **Risk Classification**: Automatically categorizes AI systems into the 4 EU AI Act risk levels

### 🔌 **MCP Server Integration** 
- **Gradio API Endpoints**: Functions are automatically exposed as API endpoints
- **4 MCP Tools** available through Gradio's API:
  - `check_compliance` - Full compliance analysis
  - `explain_compliance` - Detailed compliance explanation  
  - `assess_risk` - Risk level assessment
  - `get_risk_info` - EU AI Act risk categories reference

### 🎨 **Simple Interface**
- **Clean Gradio UI**: User-friendly web interface
- **Real-time Analysis**: Get compliance results in seconds
- **Visual Risk Display**: Color-coded risk level indicators

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- **Anthropic API key** (get from [console.anthropic.com](https://console.anthropic.com))
- **EU AI Act PDF** (place as `eu_ai_act.pdf` in project root)

### Quick Start

1. **Clone and Install**
```bash
git clone <your-repo>
cd eu-ai-act-compliance-checker
pip install -r requirements.txt
```

2. **Set up API Key**
```bash
# Copy the template and add your key
cp env_template.txt .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
```

3. **Add EU AI Act PDF**
```bash
# Place the EU AI Act PDF as 'eu_ai_act.pdf' in the project root
# The app will read the first 20 pages for key articles
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
      "args": ["/path/to/your/app.py"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key"
      }
    }
  }
}
```

**Alternative: Use Gradio API endpoints directly**
```json
{
  "mcpServers": {
    "gradio-eu-ai-act": {
      "url": "http://localhost:7860/api/predict/"
    }
  }
}
```

#### Cursor IDE  
1. Install MCP extension
2. Add server configuration pointing to your app.py

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

### ℹ️ **Limited Risk** (Transparency Required)
- Chatbots & conversational AI
- Emotion recognition
- AI-generated content

### ✅ **Minimal Risk** (No Specific Obligations)
- AI games and filters
- Simple recommendation systems

## 🚀 Available MCP Tools

| Tool Name | Description | Input | Output |
|-----------|-------------|--------|--------|
| `check_compliance` | Full compliance analysis | `scenario: string` | Complete compliance report |
| `explain_compliance` | Detailed compliance explanation | `scenario: string` | Detailed analysis with requirements |
| `assess_risk` | Risk level assessment only | `scenario: string` | Risk classification and explanation |
| `get_risk_info` | EU AI Act risk categories info | None | Risk categories reference |

## 🏗️ Technical Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gradio App    │    │   Built-in MCP   │    │  Anthropic      │
│   Interface     │◄──►│   Server         │◄──►│  Claude API     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  EU AI Act      │    │   MCP Tools      │    │  PDF Content    │
│  Compliance     │    │   (4 tools)     │    │  Processing     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📝 Example Usage

### Web Interface
1. Enter your AI use case scenario
2. Click "🔍 Analyze Compliance"  
3. Get risk level, compliance status, and recommendations

### MCP Integration
```python
# Available through MCP clients like Claude Desktop
"Check if this chatbot complies with EU AI Act"
# → Uses check_compliance tool automatically
```

## 🎯 Hackathon Submission

**Track:** MCP Server/Tool Track  
**Demo:** This Space serves as both a functional web app and MCP server

**Key Innovation:** Demonstrates how Gradio apps can serve as powerful MCP servers using the built-in `mcp_server=True` functionality, extending AI assistants with specialized EU AI Act compliance knowledge.

## 📁 Project Structure

```
eu-ai-act-compliance-checker/
├── app.py                    # Main application (Gradio + MCP server)
├── requirements.txt          # Minimal dependencies
├── env_template.txt         # Environment variables template
├── eu_ai_act.pdf           # EU AI Act document (required)
├── README.md               # This file
└── hackathon.md           # Hackathon documentation
```

## 🏆 Built for Hackathon

This simplified version focuses on:
- ✅ **Core functionality** - EU AI Act compliance checking
- ✅ **MCP integration** - Using Gradio's built-in MCP server
- ✅ **Anthropic API** - Leveraging Claude for analysis
- ✅ **Simple setup** - Minimal dependencies and configuration
- ✅ **Hackathon ready** - Quick to deploy and demonstrate

---

**🎊 Gradio Agents & MCP Hackathon 2025** | **MCP Server Track**  
*Making EU AI Act compliance accessible through AI assistants!* 