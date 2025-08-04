#!/usr/bin/env python3
"""
Debug script to test validation with actual data files
"""

import sys
import os
import json

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_with_actual_data():
    """Test validation with the actual MVR and Quote data"""
    
    # Load the actual data files
    with open('backend/mvr_result.json', 'r') as f:
        mvr_data = json.load(f)
    
    with open('backend/quote_result.json', 'r') as f:
        quote_data = json.load(f)
    
    print("=== ACTUAL DATA ANALYSIS ===")
    print(f"MVR Data:")
    print(f"  License: {mvr_data.get('licence_number')}")
    print(f"  Name: {mvr_data.get('name')}")
    print(f"  Birth Date: {mvr_data.get('birth_date')}")
    print(f"  Expiry Date: {mvr_data.get('expiry_date')}")
    print(f"  Issue Date: {mvr_data.get('issue_date')}")
    
    print(f"\nQuote Data:")
    print(f"  Quote Effective Date: {quote_data.get('quote_effective_date')}")
    print(f"  Applicant: {quote_data.get('applicant', {}).get('first_name')} {quote_data.get('applicant', {}).get('last_name')}")
    
    if quote_data.get('drivers'):
        driver = quote_data['drivers'][0]
        print(f"  Driver: {driver.get('full_name')}")
        print(f"  Birth Date: {driver.get('birth_date')}")
        print(f"  License Number: {driver.get('licence_number')}")
        print(f"  License Class: {driver.get('licence_class')}")
        print(f"  G1 Date: {driver.get('date_g1')}")
        print(f"  G2 Date: {driver.get('date_g2')}")
        print(f"  G Date: {driver.get('date_g')}")
    
    # Test the validation engine
    engine = ValidationEngine()
    
    # Create test data structure
    test_data = {
        "extracted": {
            "quotes": [quote_data],
            "mvrs": [mvr_data],
            "dashes": []
        }
    }
    
    print("\n=== VALIDATION TEST ===")
    result = engine.validate_quote(test_data)
    
    print(f"Summary:")
    print(f"  Total Drivers: {result['summary']['total_drivers']}")
    print(f"  Validated Drivers: {result['summary']['validated_drivers']}")
    print(f"  Issues Found: {result['summary']['issues_found']}")
    print(f"  Critical Errors: {result['summary']['critical_errors']}")
    print(f"  Warnings: {result['summary']['warnings']}")
    
    if result.get('drivers'):
        driver_result = result['drivers'][0]
        print(f"\nDriver Validation:")
        print(f"  Driver Name: {driver_result.get('driver_name')}")
        print(f"  Driver License: {driver_result.get('driver_license')}")
        print(f"  Validation Status: {driver_result.get('validation_status')}")
        
        # Check MVR validation
        mvr_val = driver_result.get('mvr_validation', {})
        print(f"\nMVR Validation:")
        print(f"  Status: {mvr_val.get('status')}")
        print(f"  Critical Errors: {len(mvr_val.get('critical_errors', []))}")
        print(f"  Warnings: {len(mvr_val.get('warnings', []))}")
        print(f"  Matches: {len(mvr_val.get('matches', []))}")
        
        if mvr_val.get('critical_errors'):
            print("  🟥 Critical Errors:")
            for error in mvr_val['critical_errors']:
                print(f"    • {error}")
        
        if mvr_val.get('warnings'):
            print("  🟧 Warnings:")
            for warning in mvr_val['warnings']:
                print(f"    • {warning}")
        
        if mvr_val.get('matches'):
            print("  ✅ Matches:")
            for match in mvr_val['matches']:
                print(f"    • {match}")
        
        # Check License Progression validation
        lic_val = driver_result.get('license_progression_validation', {})
        print(f"\nLicense Progression Validation:")
        print(f"  Status: {lic_val.get('status')}")
        print(f"  Critical Errors: {len(lic_val.get('critical_errors', []))}")
        print(f"  Warnings: {len(lic_val.get('warnings', []))}")
        print(f"  Matches: {len(lic_val.get('matches', []))}")
        
        if lic_val.get('critical_errors'):
            print("  🟥 Critical Errors:")
            for error in lic_val['critical_errors']:
                print(f"    • {error}")
        
        if lic_val.get('warnings'):
            print("  🟧 Warnings:")
            for warning in lic_val['warnings']:
                print(f"    • {warning}")
        
        if lic_val.get('matches'):
            print("  ✅ Matches:")
            for match in lic_val['matches']:
                print(f"    • {match}")

def test_date_parsing():
    """Test date parsing with the actual dates"""
    
    engine = ValidationEngine()
    
    # Test the actual dates from the data
    test_dates = [
        ("MVR birth_date", "04/08/1965", "mvr"),
        ("Quote birth_date", "08/04/1965", "quote"),
        ("Quote G1", "07/08/2002", "quote"),
        ("Quote G2", "07/08/2003", "quote"),
        ("Quote G", "07/08/2004", "quote"),
        ("MVR expiry", "04/08/2025", "mvr"),
        ("MVR issue", "08/07/2002", "mvr")
    ]
    
    print("\n=== DATE PARSING TEST ===")
    for name, date_str, source_type in test_dates:
        parsed = engine._parse_date(date_str, source_type)
        normalized = engine._normalize_date(date_str, source_type)
        print(f"{name}: {date_str} -> Parsed: {parsed}, Normalized: {normalized}")

if __name__ == "__main__":
    test_date_parsing()
    test_with_actual_data() 