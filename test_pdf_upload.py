#!/usr/bin/env python3
"""
Test script to verify Anthropic PDF upload functionality
"""

import asyncio
import os
import sys
from compliance_checker import ComplianceChecker
from document_processor import EUAIActProcessor

async def test_anthropic_pdf_upload():
    """Test the Anthropic PDF upload and analysis functionality"""
    
    print("🧪 Testing Anthropic PDF Upload & Analysis...")
    print("=" * 60)
    
    # Check prerequisites
    if not os.path.exists("eu_ai_act.pdf"):
        print("❌ EU AI Act PDF not found. Please place 'eu_ai_act.pdf' in the project root.")
        return False
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not set. Please set your Anthropic API key.")
        return False
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        processor = EUAIActProcessor()
        checker = ComplianceChecker()
        
        await processor.initialize()
        await checker.initialize(processor)
        
        # Check if PDF was uploaded to Anthropic
        if checker.pdf_file_id:
            print(f"✅ PDF successfully uploaded to Anthropic. File ID: {checker.pdf_file_id}")
        else:
            print("⚠️ PDF not uploaded to Anthropic. Using semantic search fallback.")
            return False
        
        # Test compliance analysis with PDF
        test_scenario = "We are developing a facial recognition system for employee attendance tracking in our office building."
        
        print(f"\n🎯 Testing scenario: {test_scenario}")
        print("🔄 Analyzing with Anthropic PDF support...")
        
        result = await checker.check_compliance(test_scenario)
        
        if result.get("error"):
            print(f"❌ Analysis failed: {result['error']}")
            return False
        
        # Display results
        print("\n📊 Analysis Results:")
        print(f"Analysis Method: {result.get('analysis_method', 'unknown')}")
        
        risk_level = result.get("risk_level", {})
        print(f"Risk Category: {risk_level.get('category', 'Unknown')}")
        
        cited_articles = risk_level.get("cited_articles", [])
        if cited_articles:
            print(f"Cited Articles: {', '.join(cited_articles)}")
        
        regulatory_basis = risk_level.get("regulatory_basis", "")
        if regulatory_basis:
            print(f"Regulatory Basis: {regulatory_basis[:200]}...")
        
        compliance = result.get("compliance", {})
        print(f"Compliance: {'✅ COMPLIANT' if compliance.get('compliant') else '⚠️ NON-COMPLIANT'}")
        
        applicable_articles = compliance.get("applicable_articles", [])
        if applicable_articles:
            print(f"Applicable Articles: {', '.join(applicable_articles)}")
        
        print("\n🎉 Anthropic PDF analysis completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

async def test_comparison():
    """Compare PDF analysis vs semantic search results"""
    
    print("\n🔄 Comparing Analysis Methods...")
    print("=" * 60)
    
    test_scenario = "We want to implement an AI chatbot for customer service."
    
    try:
        # Test with Anthropic PDF
        processor = EUAIActProcessor()
        checker = ComplianceChecker()
        
        await processor.initialize()
        await checker.initialize(processor)
        
        result_pdf = await checker.check_compliance(test_scenario)
        
        print(f"📊 PDF Analysis Method: {result_pdf.get('analysis_method')}")
        print(f"Risk Category: {result_pdf.get('risk_level', {}).get('category')}")
        print(f"Has Cited Articles: {'Yes' if result_pdf.get('risk_level', {}).get('cited_articles') else 'No'}")
        print(f"Has Regulatory Basis: {'Yes' if result_pdf.get('risk_level', {}).get('regulatory_basis') else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Comparison failed: {str(e)}")
        return False

if __name__ == "__main__":
    async def run_tests():
        success = await test_anthropic_pdf_upload()
        if success:
            await test_comparison()
        return success
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1) 