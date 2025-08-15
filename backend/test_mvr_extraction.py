#!/usr/bin/env python3
"""
Test script to debug MVR extraction and validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractors.mvr_extractor import extract_mvr_data
from validator.compare_engine import ValidationEngine

def test_mvr_extraction(mvr_path):
    """Test MVR extraction and validation"""
    print(f"Testing MVR extraction for: {mvr_path}")
    print("=" * 50)
    
    # Extract MVR data
    try:
        mvr_data = extract_mvr_data(mvr_path)
        print("Extracted MVR Data:")
        print(f"  Name: {mvr_data.get('name', 'N/A')}")
        print(f"  License Number: {mvr_data.get('licence_number', 'N/A')}")
        print(f"  Birth Date: {mvr_data.get('birth_date', 'N/A')}")
        print(f"  Expiry Date: {mvr_data.get('expiry_date', 'N/A')}")
        print(f"  Issue Date: {mvr_data.get('issue_date', 'N/A')}")
        print(f"  Release Date: {mvr_data.get('release_date', 'N/A')}")
        print(f"  Status: {mvr_data.get('status', 'N/A')}")
        print(f"  Address: {mvr_data.get('address', 'N/A')}")
        print(f"  Convictions: {len(mvr_data.get('convictions', []))}")
        
        # Test license progression validation
        print("\n" + "=" * 50)
        print("Testing License Progression Validation:")
        
        # Create a mock driver for testing
        mock_driver = {
            "driver_name": mvr_data.get('name', 'Test Driver'),
            "driver_license": mvr_data.get('licence_number', 'TEST123'),
            "date_g1": "",  # No G1 date provided
            "date_g2": "",  # No G2 date provided
            "date_g": "04/21/1994",   # G date that matches the MVR issue date
            "licence_class": "G"  # Default to G class
        }
        
        # Create validation engine
        validation_engine = ValidationEngine()
        
        # Test validation
        validation_result = validation_engine._validate_license_progression_enhanced(mock_driver, mvr_data)
        
        print(f"Validation Status: {validation_result['status']}")
        print(f"Critical Errors: {len(validation_result['critical_errors'])}")
        print(f"Warnings: {len(validation_result['warnings'])}")
        print(f"Matches: {len(validation_result['matches'])}")
        
        if validation_result['critical_errors']:
            print("\nCritical Errors:")
            for error in validation_result['critical_errors']:
                print(f"  [ERROR] {error}")
        
        if validation_result['warnings']:
            print("\nWarnings:")
            for warning in validation_result['warnings']:
                print(f"  [WARNING] {warning}")
        
        if validation_result['matches']:
            print("\nMatches:")
            for match in validation_result['matches']:
                print(f"  [MATCH] {match}")
        
    except Exception as e:
        print(f"Error testing MVR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_mvr_extraction.py <path_to_mvr_pdf>")
        sys.exit(1)
    
    mvr_path = sys.argv[1]
    if not os.path.exists(mvr_path):
        print(f"Error: File {mvr_path} does not exist")
        sys.exit(1)
    
    test_mvr_extraction(mvr_path)
