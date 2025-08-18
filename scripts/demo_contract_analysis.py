#!/usr/bin/env python3
"""
Demo Contract Analysis for ContractGuard.ai
Shows generated test contracts and simulates AI analysis workflow
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List, Any

def load_contract_content(file_path: str) -> str:
    """Load contract content from file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error loading file: {e}"

def simulate_ai_analysis(contract_content: str, category: str) -> Dict[str, Any]:
    """Simulate AI analysis results."""
    
    # Simulate analysis time
    analysis_time = random.uniform(2.0, 8.0)
    
    # Generate realistic analysis based on category
    if category == "NDA":
        risks = [
            {"severity": 4, "title": "Overly Broad Confidentiality", "description": "Confidentiality obligations extend beyond reasonable business needs"},
            {"severity": 3, "title": "Unlimited Term", "description": "No clear expiration date for confidentiality obligations"},
            {"severity": 2, "title": "No Carve-outs", "description": "Missing exceptions for publicly available information"}
        ]
        suggestions = [
            "Limit confidentiality scope to specific business purposes",
            "Add reasonable term limits (2-5 years)",
            "Include carve-outs for public information and independent development"
        ]
    elif category == "MSA":
        risks = [
            {"severity": 5, "title": "Unlimited Liability", "description": "No liability caps could expose company to significant financial risk"},
            {"severity": 4, "title": "Auto-renewal", "description": "Contract automatically renews without explicit consent"},
            {"severity": 3, "title": "Broad Indemnity", "description": "One-sided indemnification obligations"}
        ]
        suggestions = [
            "Add reasonable liability caps (e.g., 12 months of fees)",
            "Require explicit renewal consent",
            "Limit indemnity to direct damages and negligence"
        ]
    elif category == "SOW":
        risks = [
            {"severity": 4, "title": "Vague Deliverables", "description": "Unclear acceptance criteria for project completion"},
            {"severity": 3, "title": "Unrealistic Timeline", "description": "Project timeline may not be achievable"},
            {"severity": 3, "title": "Scope Creep Risk", "description": "No clear change management process"}
        ]
        suggestions = [
            "Define specific, measurable deliverables",
            "Include milestone-based payment schedule",
            "Establish formal change order procedures"
        ]
    elif category == "Employment":
        risks = [
            {"severity": 4, "title": "Unfavorable Termination", "description": "One-sided termination provisions"},
            {"severity": 3, "title": "Broad Non-compete", "description": "Overly restrictive non-competition terms"},
            {"severity": 2, "title": "Unclear IP Ownership", "description": "Ambiguous intellectual property rights"}
        ]
        suggestions = [
            "Ensure mutual termination rights",
            "Limit non-compete to reasonable scope and duration",
            "Clearly define IP ownership and assignment"
        ]
    elif category == "Vendor":
        risks = [
            {"severity": 4, "title": "No Performance Guarantees", "description": "Missing service level agreements"},
            {"severity": 3, "title": "Unfavorable Payment Terms", "description": "Payment schedule may impact cash flow"},
            {"severity": 3, "title": "Limited Liability", "description": "Vendor liability may be too restrictive"}
        ]
        suggestions = [
            "Include specific SLA requirements",
            "Negotiate favorable payment terms",
            "Ensure reasonable liability provisions"
        ]
    elif category == "Lease":
        risks = [
            {"severity": 4, "title": "Auto-renewal", "description": "Lease automatically renews without notice"},
            {"severity": 3, "title": "Unfavorable Maintenance", "description": "Tenant responsible for major repairs"},
            {"severity": 3, "title": "Rent Escalation", "description": "Unreasonable rent increase provisions"}
        ]
        suggestions = [
            "Require explicit renewal consent",
            "Limit tenant maintenance obligations",
            "Cap rent increases to reasonable percentages"
        ]
    else:  # Other
        risks = [
            {"severity": 3, "title": "Unclear Obligations", "description": "Vague responsibilities for each party"},
            {"severity": 3, "title": "Limited Remedies", "description": "Insufficient recourse for breaches"},
            {"severity": 2, "title": "Unfavorable Terms", "description": "One-sided agreement terms"}
        ]
        suggestions = [
            "Define specific obligations clearly",
            "Include adequate remedy provisions",
            "Ensure balanced agreement terms"
        ]
    
    return {
        "analysis_time_seconds": round(analysis_time, 2),
        "summary": f"AI analysis completed for {category} contract in {analysis_time:.1f} seconds",
        "risks": risks,
        "suggestions": suggestions,
        "confidence_score": round(random.uniform(0.85, 0.98), 2),
        "risk_score": round(random.uniform(0.3, 0.7), 2)
    }

def main():
    """Main demo function."""
    print("🚀 ContractGuard.ai - Demo Contract Analysis")
    print("=" * 60)
    
    # Check if test contracts directory exists
    test_contracts_dir = "test_contracts"
    if not os.path.exists(test_contracts_dir):
        print(f"❌ Test contracts directory '{test_contracts_dir}' not found!")
        print("Please run 'generate_test_contracts_simple.py' first to generate test contracts.")
        return
    
    # Get list of contract files
    contract_files = [f for f in os.listdir(test_contracts_dir) if f.endswith('.txt')]
    contract_files.sort()
    
    if not contract_files:
        print(f"❌ No contract files found in '{test_contracts_dir}' directory!")
        return
    
    print(f"\n📄 Found {len(contract_files)} contract files to analyze")
    print("🔍 Simulating AI analysis workflow...")
    print("=" * 60)
    
    # Process each contract
    total_analysis_time = 0
    total_risks = 0
    total_suggestions = 0
    category_counts = {}
    
    for i, filename in enumerate(contract_files, 1):
        print(f"\n📄 Processing contract {i}/{len(contract_files)}: {filename}")
        print("-" * 50)
        
        # Extract category from filename
        category = filename.split('_')[0]
        category_counts[category] = category_counts.get(category, 0) + 1
        
        # Load contract content
        file_path = os.path.join(test_contracts_dir, filename)
        contract_content = load_contract_content(file_path)
        
        # Show contract preview
        preview = contract_content[:200] + "..." if len(contract_content) > 200 else contract_content
        print(f"📋 Category: {category}")
        print(f"📝 Content Preview: {preview}")
        
        # Simulate AI analysis
        print(f"🤖 Running AI analysis...")
        analysis_results = simulate_ai_analysis(contract_content, category)
        
        # Display results
        print(f"✅ Analysis completed in {analysis_results['analysis_time_seconds']}s")
        print(f"🎯 Confidence Score: {analysis_results['confidence_score']}")
        print(f"⚠️  Risk Score: {analysis_results['risk_score']}")
        
        # Show top risks
        print(f"🚨 Top Risks:")
        for risk in analysis_results['risks'][:2]:  # Show top 2 risks
            print(f"   • {risk['title']} (Severity: {risk['severity']})")
        
        # Show suggestions
        print(f"💡 Key Suggestions:")
        for suggestion in analysis_results['suggestions'][:2]:  # Show top 2 suggestions
            print(f"   • {suggestion}")
        
        # Accumulate stats
        total_analysis_time += analysis_results['analysis_time_seconds']
        total_risks += len(analysis_results['risks'])
        total_suggestions += len(analysis_results['suggestions'])
        
        # Small delay for demo effect
        import time
        time.sleep(0.5)
    
    # Summary
    print(f"\n🎉 Demo Analysis Complete!")
    print("=" * 60)
    print(f"📊 Summary Statistics:")
    print(f"   • Total contracts analyzed: {len(contract_files)}")
    print(f"   • Total analysis time: {total_analysis_time:.1f} seconds")
    print(f"   • Average analysis time: {total_analysis_time/len(contract_files):.1f} seconds")
    print(f"   • Total risks identified: {total_risks}")
    print(f"   • Total suggestions generated: {total_suggestions}")
    
    print(f"\n📈 Category Distribution:")
    for category, count in sorted(category_counts.items()):
        print(f"   • {category}: {count} contracts")
    
    print(f"\n🔍 What This Demonstrates:")
    print(f"   1. ✅ Contract Generation: Realistic test contracts for all categories")
    print(f"   2. ✅ Content Variety: 19 unique contracts with different scenarios")
    print(f"   3. ✅ AI Analysis: Simulated risk assessment and suggestions")
    print(f"   4. ✅ Category Coverage: All 7 contract types supported")
    print(f"   5. ✅ Training Data: Perfect for AI model training")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Fix backend API issues to enable real contract uploads")
    print(f"   2. Integrate with actual AI analysis engine")
    print(f"   3. Use generated contracts for AI model training")
    print(f"   4. Run analysis on real contracts through the system")
    
    print(f"\n💡 Key Benefits of This Approach:")
    print(f"   • Text files are perfect for AI training (no PDF complexity)")
    print(f"   • Easy to modify and generate new scenarios")
    print(f"   • Consistent format for systematic analysis")
    print(f"   • Fast generation for large training datasets")

if __name__ == "__main__":
    main()
