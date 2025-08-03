#!/usr/bin/env python3
"""
Test script to demonstrate claim field extraction from dash reports.
"""

import sys
import os

# Add the backend directory to the path so we can import the extractor
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from extractors.dash_extractor import extract_and_save_claim_fields, extract_specific_claim_fields

def main():
    """Main function to test claim field extraction."""
    
    print("=== DASH CLAIM FIELD EXTRACTION TEST ===\n")
    
    # Test with the existing JSON file
    json_file = 'backend/dash_result.json'
    
    if os.path.exists(json_file):
        print(f"Testing with existing file: {json_file}")
        extracted_claims = extract_and_save_claim_fields(json_file)
        
        if extracted_claims:
            print(f"\n✅ Successfully extracted {len(extracted_claims)} claims")
            print("Files created:")
            print("  - extracted_claims.csv")
            print("  - extracted_claims.json")
        else:
            print("❌ Failed to extract claims")
    else:
        print(f"❌ File not found: {json_file}")
        print("Please run the dash extractor first to generate the JSON file.")
    
    print("\n=== USAGE INSTRUCTIONS ===")
    print("1. To extract from a PDF file:")
    print("   from extractors.dash_extractor import extract_dash_data")
    print("   result = extract_dash_data('your_pdf_file.pdf')")
    print("")
    print("2. To extract specific claim fields from JSON:")
    print("   from extractors.dash_extractor import extract_and_save_claim_fields")
    print("   claims = extract_and_save_claim_fields('dash_result.json')")
    print("")
    print("3. To extract fields programmatically:")
    print("   from extractors.dash_extractor import extract_specific_claim_fields")
    print("   import json")
    print("   with open('dash_result.json', 'r') as f:")
    print("       data = json.load(f)")
    print("   claims = extract_specific_claim_fields(data)")

if __name__ == "__main__":
    main() 