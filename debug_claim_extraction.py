#!/usr/bin/env python3
"""
Debug script to help identify why the First Party Driver field isn't being extracted correctly.
"""

import sys
import os
import re

# Add the backend directory to the path so we can import the extractor
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def debug_pdf_text():
    """Debug the PDF text to see what's actually there."""
    
    # Check if Dash_test.txt exists
    if os.path.exists("Dash_test.txt"):
        print("=== ANALYZING PDF TEXT ===")
        with open("Dash_test.txt", "r", encoding="utf-8") as f:
            text = f.read()
        
        print(f"Total text length: {len(text)} characters")
        
        # Look for First Party Driver patterns
        print("\n=== SEARCHING FOR FIRST PARTY DRIVER PATTERNS ===")
        
        patterns_to_search = [
            r'First Party Driver Listed on Policy:\s*(Yes|No|True|False)',
            r'First Party Driver:\s*(Yes|No|True|False)',
            r'First Party Driver:\s*([^\n]+)',
            r'Driver Listed on Policy:\s*(Yes|No|True|False)',
            r'Driver:\s*(Yes|No|True|False)',
            r'At-Fault:\s*(Yes|No|True|False)',
            r'Total Loss:\s*\$?([\d,]+\.?\d*)',
            r'Claim Status:\s*([^\n]+)'
        ]
        
        for pattern in patterns_to_search:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                print(f"✅ Found '{pattern}': {matches}")
            else:
                print(f"❌ Not found: '{pattern}'")
        
        # Look for claim sections
        print("\n=== SEARCHING FOR CLAIM SECTIONS ===")
        claim_sections = re.findall(r'Claim #(\d+).*?(?=Claim #\d+|Page \d+|$)', text, re.DOTALL | re.IGNORECASE)
        print(f"Found {len(claim_sections)} claim sections")
        
        for i, section in enumerate(claim_sections[:3]):  # Show first 3
            print(f"\nClaim section {i+1} (first 200 chars):")
            print(repr(section[:200]))
        
        # Look for the specific text mentioned by user
        print("\n=== SEARCHING FOR SPECIFIC TEXT ===")
        specific_patterns = [
            r'First Party Driver Listed on Policy:\s*Yes',
            r'First Party Driver Listed on Policy:\s*No',
            r'First Party Driver.*?Yes',
            r'First Party Driver.*?No'
        ]
        
        for pattern in specific_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                print(f"✅ Found: '{pattern}'")
                for match in matches:
                    print(f"   Match: '{match}'")
            else:
                print(f"❌ Not found: '{pattern}'")
        
        # Show context around "First Party Driver"
        print("\n=== CONTEXT AROUND 'FIRST PARTY DRIVER' ===")
        context_matches = re.findall(r'.{0,50}First Party Driver.{0,50}', text, re.IGNORECASE)
        for i, match in enumerate(context_matches[:5]):  # Show first 5
            print(f"Context {i+1}: '{match}'")
            
    else:
        print("❌ Dash_test.txt not found. Please run the dash extractor first.")

def test_enhanced_extraction():
    """Test the enhanced extraction function."""
    try:
        from extractors.dash_extractor import extract_and_save_claim_fields
        
        print("\n=== TESTING ENHANCED EXTRACTION ===")
        json_file = 'backend/dash_result.json'
        
        if os.path.exists(json_file):
            claims = extract_and_save_claim_fields(json_file)
            if claims:
                print(f"✅ Enhanced extraction completed: {len(claims)} claims processed")
                return True
        else:
            print("❌ dash_result.json not found")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced extraction test failed: {e}")
        return False

def main():
    """Main debug function."""
    print("=== CLAIM EXTRACTION DEBUG ===\n")
    
    # Debug the PDF text
    debug_pdf_text()
    
    # Test enhanced extraction
    test_enhanced_extraction()
    
    print("\n=== DEBUG COMPLETE ===")
    print("Check the output above to see what patterns are found in the PDF text.")

if __name__ == "__main__":
    main() 