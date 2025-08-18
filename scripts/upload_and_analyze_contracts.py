#!/usr/bin/env python3
"""
Upload and Analyze Test Contracts for ContractGuard.ai
Automatically uploads generated test contracts and runs AI analysis
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Any

# API Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
CONTRACTS_URL = f"{BASE_URL}/api"
UPLOAD_URL = f"{BASE_URL}/api/upload"
ANALYZE_URL = f"{BASE_URL}/api/analyze"

def login_user(username: str, password: str) -> str:
    """Login user and return JWT token."""
    try:
        print(f"🔐 Logging in as {username}...")
        response = requests.post(LOGIN_URL, data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Successfully logged in as {username}")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def create_contract(token: str, contract_data: Dict[str, Any]) -> int:
    """Create a contract and return its ID."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create contract record
        contract_payload = {
            "title": contract_data["title"],
            "counterparty": contract_data["counterparty"],
            "category": contract_data["category"],
            "effective_date": contract_data["effective_date"],
            "term_end": contract_data["term_end"],
            "governing_law": contract_data["governing_law"]
        }
        
        print(f"📝 Creating contract: {contract_data['title']}")
        response = requests.post(f"{CONTRACTS_URL}/", json=contract_payload, headers=headers)
        
        if response.status_code == 200:
            contract_id = response.json()["id"]
            print(f"✅ Created contract (ID: {contract_id})")
            return contract_id
        else:
            print(f"❌ Contract creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Contract creation error: {e}")
        return None

def upload_contract_file(token: str, contract_id: int, file_path: str) -> bool:
    """Upload contract file."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"📁 Uploading file: {os.path.basename(file_path)}")
        
        # Upload file
        with open(file_path, 'rb') as f:
            filename = os.path.basename(file_path)
            files = {"file": (filename, f, "text/plain")}
            response = requests.post(f"{UPLOAD_URL}/{contract_id}", files=files, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ File uploaded successfully")
            return True
        else:
            print(f"❌ File upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return False

def analyze_contract(token: str, contract_id: int) -> bool:
    """Trigger contract analysis."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"🤖 Triggering AI analysis...")
        response = requests.post(f"{ANALYZE_URL}/{contract_id}", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Analysis triggered successfully")
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def extract_contract_info_from_filename(filename: str) -> Dict[str, str]:
    """Extract contract information from filename."""
    # Format: Category_Number_Counterparty.txt
    parts = filename.replace('.txt', '').split('_')
    
    if len(parts) >= 3:
        category = parts[0]
        number = parts[1]
        counterparty = '_'.join(parts[2:])  # Handle multi-word company names
        
        return {
            "category": category,
            "number": number,
            "counterparty": counterparty
        }
    else:
        return {
            "category": "Other",
            "number": "1",
            "counterparty": "Unknown"
        }

def generate_contract_data(category: str, counterparty: str) -> Dict[str, Any]:
    """Generate contract metadata based on category and counterparty."""
    import random
    from datetime import datetime, timedelta
    
    # Generate random dates
    start_date = datetime.now() - timedelta(days=random.randint(0, 365))
    end_date = start_date + timedelta(days=random.randint(365, 1825))
    
    # Generate title based on category
    titles = {
        "NDA": ["Confidentiality Agreement", "Non-Disclosure Agreement", "Proprietary Information Agreement"],
        "MSA": ["Master Services Agreement", "Service Agreement", "Professional Services Agreement"],
        "SOW": ["Statement of Work", "Project Agreement", "Work Order"],
        "Employment": ["Employment Agreement", "Employment Contract", "Offer Letter"],
        "Vendor": ["Vendor Agreement", "Supplier Contract", "Service Provider Agreement"],
        "Lease": ["Lease Agreement", "Rental Contract", "Property Lease"],
        "Other": ["Service Agreement", "Business Agreement", "Partnership Agreement"]
    }
    
    title = f"{random.choice(titles.get(category, ['Agreement']))} - {counterparty}"
    
    return {
        "title": title,
        "counterparty": counterparty,
        "category": category,
        "effective_date": start_date.strftime("%Y-%m-%dT%H:%M:%S"),  # ISO format with T separator
        "term_end": end_date.strftime("%Y-%m-%dT%H:%M:%S"),  # ISO format with T separator
        "governing_law": random.choice(["California", "New York", "Delaware", "Texas", "Florida"])
    }

def main():
    """Main function to upload and analyze test contracts."""
    print("🚀 ContractGuard.ai - Test Contract Upload & Analysis")
    print("=" * 60)
    
    # Check if test contracts directory exists
    test_contracts_dir = "test_contracts"
    if not os.path.exists(test_contracts_dir):
        print(f"❌ Test contracts directory '{test_contracts_dir}' not found!")
        print("Please run 'generate_test_contracts_simple.py' first to generate test contracts.")
        return
    
    # Login
    token = login_user("admin", "test123")
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Get list of contract files
    contract_files = [f for f in os.listdir(test_contracts_dir) if f.endswith('.txt')]
    contract_files.sort()  # Sort for consistent processing order
    
    if not contract_files:
        print(f"❌ No contract files found in '{test_contracts_dir}' directory!")
        return
    
    print(f"\n📄 Found {len(contract_files)} contract files to process")
    print("=" * 60)
    
    # Process each contract file
    successful_uploads = 0
    successful_analyses = 0
    
    for i, filename in enumerate(contract_files, 1):
        print(f"\n📄 Processing contract {i}/{len(contract_files)}: {filename}")
        print("-" * 50)
        
        file_path = os.path.join(test_contracts_dir, filename)
        
        # Extract contract information from filename
        contract_info = extract_contract_info_from_filename(filename)
        print(f"📋 Category: {contract_info['category']}")
        print(f"🏢 Counterparty: {contract_info['counterparty']}")
        
        # Generate contract metadata
        contract_data = generate_contract_data(contract_info['category'], contract_info['counterparty'])
        
        # Create contract record
        contract_id = create_contract(token, contract_data)
        if not contract_id:
            print(f"❌ Skipping {filename} due to creation failure")
            continue
        
        # Upload contract file
        if upload_contract_file(token, contract_id, file_path):
            successful_uploads += 1
            
            # Trigger analysis
            if analyze_contract(token, contract_id):
                successful_analyses += 1
            
            # Small delay between contracts
            time.sleep(2)
        else:
            print(f"❌ Skipping analysis for {filename} due to upload failure")
    
    # Summary
    print(f"\n🎉 Contract processing complete!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   • Total contracts: {len(contract_files)}")
    print(f"   • Successfully uploaded: {successful_uploads}")
    print(f"   • Successfully analyzed: {successful_analyses}")
    print(f"   • Success rate: {(successful_uploads/len(contract_files)*100):.1f}%")
    
    if successful_analyses > 0:
        print(f"\n🔍 Next steps:")
        print(f"   1. Check the ContractGuard.ai dashboard to see uploaded contracts")
        print(f"   2. Review AI analysis results and risk assessments")
        print(f"   3. Analyze the quality and accuracy of AI insights")
        print(f"   4. Use results to improve the AI model training")
        print(f"   5. Run the script again to generate more training data")
    else:
        print(f"\n⚠️  No contracts were successfully analyzed. Check the logs above for errors.")

if __name__ == "__main__":
    main()
