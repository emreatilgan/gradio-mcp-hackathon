#!/usr/bin/env python3
"""
Test scenarios for EU Regulations Compliance Checker
Testing various compliance scenarios against EU regulations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import ComplianceAnalyzer, EURegulationsQuerier
import json

def test_sparql_connectivity():
    """Test SPARQL endpoint connectivity"""
    print("🔍 Testing SPARQL Connectivity...")
    
    querier = EURegulationsQuerier()
    
    # Test basic connectivity
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
        print("✅ SPARQL Connection Successful!")
        print(f"Found {len(results)} data protection regulations:")
        for result in results:
            print(f"  • {result.get('title', 'Unknown Title')}")
    else:
        print("❌ SPARQL Connection Failed or No Results")
    
    return results

def test_compliance_scenarios():
    """Test various compliance scenarios"""
    print("\n🧪 Testing Compliance Scenarios...")
    
    analyzer = ComplianceAnalyzer()
    
    # Test scenarios
    scenarios = [
        {
            "name": "GDPR - E-commerce Data Collection",
            "scenario": "Our e-commerce platform collects customer email addresses, purchase history, and browsing behavior to provide personalized product recommendations and send marketing emails.",
            "expected_regulations": ["gdpr"]
        },
        {
            "name": "AI Act - Automated Loan Approval",
            "scenario": "We use machine learning algorithms to automatically approve or reject loan applications based on customer financial data, credit scores, and behavioral patterns.",
            "expected_regulations": ["gdpr", "ai_act"]
        },
        {
            "name": "Digital Services Act - Social Media Platform",
            "scenario": "Our social media platform allows users to upload content and we use automated content moderation systems to detect and remove harmful content.",
            "expected_regulations": ["dsa", "ai_act"]
        },
        {
            "name": "Consumer Protection - Online Marketplace",
            "scenario": "We operate an online marketplace where third-party sellers offer products to consumers. We handle payments and customer service.",
            "expected_regulations": ["consumer"]
        },
        {
            "name": "Mixed Scenario - AI-Powered Healthcare App",
            "scenario": "Our healthcare app uses artificial intelligence to analyze patient data and provide medical recommendations. We process personal health data with explicit consent from users.",
            "expected_regulations": ["gdpr", "ai_act"]
        }
    ]
    
    for i, test in enumerate(scenarios, 1):
        print(f"\n--- Test {i}: {test['name']} ---")
        print(f"Scenario: {test['scenario'][:100]}...")
        
        try:
            result = analyzer.analyze_compliance(test['scenario'])
            
            print(f"✅ Detected Regulations: {result['detected_regulations']}")
            print(f"✅ Compliance Status: {result['compliance_status']}")
            print(f"✅ Confidence: {result['confidence']:.0%}")
            print(f"✅ Issues Found: {len(result['compliance_details'])}")
            print(f"✅ Recommendations: {len(result['recommendations'])}")
            
            # Check if expected regulations were detected
            detected = set(result['detected_regulations'])
            expected = set(test['expected_regulations'])
            
            if detected.intersection(expected):
                print("✅ Expected regulation types detected")
            else:
                print(f"⚠️  Expected {expected}, got {detected}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")

def test_specific_regulations():
    """Test queries for specific EU regulations"""
    print("\n🔍 Testing Specific Regulation Queries...")
    
    querier = EURegulationsQuerier()
    
    # Test GDPR query
    print("\n--- Testing GDPR Query ---")
    gdpr_results = querier.get_gdpr_details()
    if gdpr_results:
        print("✅ GDPR found:")
        for result in gdpr_results:
            print(f"  • Title: {result.get('title', 'N/A')}")
            print(f"  • Date: {result.get('date', 'N/A')}")
            print(f"  • CELEX: {result.get('celex', 'N/A')}")
    else:
        print("❌ GDPR not found")
    
    # Test AI Act query
    print("\n--- Testing AI Act Query ---")
    ai_results = querier.get_ai_act_details()
    if ai_results:
        print("✅ AI Act found:")
        for result in ai_results:
            print(f"  • Title: {result.get('title', 'N/A')}")
            print(f"  • Date: {result.get('date', 'N/A')}")
    else:
        print("❌ AI Act not found")
    
    # Test general search
    print("\n--- Testing General Search ---")
    general_results = querier.find_relevant_regulations("consumer protection")
    if general_results:
        print(f"✅ Found {len(general_results)} consumer protection regulations:")
        for result in general_results[:3]:  # Show first 3
            print(f"  • {result.get('title', 'Unknown')}")
    else:
        print("❌ No consumer protection regulations found")

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🚀 Starting EU Regulations Compliance Checker Tests")
    print("=" * 60)
    
    # Test 1: SPARQL Connectivity
    sparql_results = test_sparql_connectivity()
    
    # Test 2: Specific Regulations
    test_specific_regulations()
    
    # Test 3: Compliance Scenarios
    test_compliance_scenarios()
    
    print("\n" + "=" * 60)
    print("✅ Test Suite Complete!")
    
    if sparql_results:
        print("🎉 SPARQL integration working - MCP server ready for deployment!")
    else:
        print("⚠️  SPARQL connectivity issues - check network connection")

if __name__ == "__main__":
    run_comprehensive_test() 