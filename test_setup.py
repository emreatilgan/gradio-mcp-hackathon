#!/usr/bin/env python3
"""
Test script to verify EU AI Act Compliance Checker setup
"""

import os
import sys

def test_requirements():
    """Test that all requirements are met"""
    print("🧪 Testing EU AI Act Compliance Checker Setup...")
    print("=" * 50)
    
    # Test 1: Check PDF document
    pdf_path = "eu_ai_act.pdf"
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
        print(f"✅ EU AI Act PDF found: {pdf_path} ({file_size:.1f} MB)")
    else:
        print(f"❌ EU AI Act PDF missing: {pdf_path}")
        print("   Please place the original 170-page EU AI Act PDF in the project root")
        return False
    
    # Test 2: Check LLM API keys
    api_keys = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"), 
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }
    
    available_keys = [key for key, value in api_keys.items() if value]
    
    if available_keys:
        print(f"✅ LLM API keys found: {', '.join(available_keys)}")
    else:
        print("❌ No LLM API keys found")
        print("   Please set at least one: ANTHROPIC_API_KEY or OPENAI_API_KEY")
        return False
    
    # Test 3: Check Python dependencies
    try:
        import gradio
        print(f"✅ Gradio: {gradio.__version__}")
    except ImportError:
        print("❌ Gradio not installed")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence Transformers available")
    except ImportError:
        print("❌ Sentence Transformers not installed")
        return False
    
    try:
        import faiss
        print("✅ FAISS available")
    except ImportError:
        print("❌ FAISS not installed")
        return False
    
    try:
        import fitz  # PyMuPDF
        print("✅ PyMuPDF available")
    except ImportError:
        print("❌ PyMuPDF not installed")
        return False
    
    # Test 4: Quick import test
    try:
        from document_processor import EUAIActProcessor
        from compliance_checker import ComplianceChecker
        print("✅ Core modules import successfully")
    except ImportError as e:
        print(f"❌ Module import failed: {e}")
        return False
    
    print("=" * 50)
    print("🎉 All requirements met! Ready to test with original EU AI Act document.")
    return True

if __name__ == "__main__":
    success = test_requirements()
    sys.exit(0 if success else 1) 