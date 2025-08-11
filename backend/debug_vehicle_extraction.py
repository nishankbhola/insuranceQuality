#!/usr/bin/env python3
"""
Debug script to analyze vehicle extraction from the specific PDF
"""
import fitz  # PyMuPDF
import re
import json
import os

def debug_vehicle_extraction(pdf_path):
    """Debug vehicle extraction from the specific PDF"""
    
    # Open PDF with PyMuPDF
    pdf_document = fitz.open(pdf_path)
    
    # Extract text from all pages
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    
    # Close the document
    pdf_document.close()
    
    print(f"Total text length: {len(text)} characters")
    
    # Look for the Described Automobile section
    described_automobile_pattern = r'Described Automobile'
    described_automobile_match = re.search(described_automobile_pattern, text, re.IGNORECASE)
    
    if described_automobile_match:
        start_pos = described_automobile_match.start()
        print(f"Found 'Described Automobile' at position {start_pos}")
        
        # Look for the next major section to determine end boundary
        next_section_patterns = [
            r'Driver Information',
            r'Claims History',
            r'Convictions',
            r'Policy Information'
        ]
        
        end_pos = len(text)
        for pattern in next_section_patterns:
            next_match = re.search(pattern, text[start_pos:], re.IGNORECASE)
            if next_match:
                end_pos = start_pos + next_match.start()
                print(f"Found next section '{pattern}' at position {end_pos}")
                break
        
        automobile_text = text[start_pos:end_pos].strip()
        print(f"Automobile section text length: {len(automobile_text)}")
        
        # Print the first and last 500 characters of the automobile section
        print("\n" + "="*80)
        print("FIRST 500 CHARACTERS OF AUTOMOBILE SECTION:")
        print("="*80)
        print(automobile_text[:500])
        
        print("\n" + "="*80)
        print("LAST 500 CHARACTERS OF AUTOMOBILE SECTION:")
        print("="*80)
        print(automobile_text[-500:])
        
        # Look for specific patterns that might contain vehicle data
        print("\n" + "="*80)
        print("SEARCHING FOR VEHICLE PATTERNS:")
        print("="*80)
        
        # Look for year patterns
        year_patterns = [
            r'(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9\s]+)',  # Year Make Model
            r'(\d{4})\s+(\d{1,2})\s*\$',  # Year Month followed by $
            r'(\d{4})\s+(\d{1,2})\s*X',   # Year Month followed by X
        ]
        
        for i, pattern in enumerate(year_patterns):
            matches = list(re.finditer(pattern, automobile_text, re.IGNORECASE))
            print(f"\nPattern {i+1}: {pattern}")
            print(f"Found {len(matches)} matches:")
            for match in matches[:5]:  # Show first 5 matches
                print(f"  Match: '{match.group()}' at position {match.start()}")
                if match.groups():
                    print(f"    Groups: {match.groups()}")
        
        # Look for VIN patterns
        vin_pattern = r'([A-Z0-9]{17})'
        vin_matches = list(re.finditer(vin_pattern, automobile_text))
        print(f"\nVIN Pattern: {vin_pattern}")
        print(f"Found {len(vin_matches)} VINs:")
        for match in vin_matches:
            print(f"  VIN: '{match.group()}' at position {match.start()}")
        
        # Look for purchase price patterns
        price_patterns = [
            r'\$([0-9,]+\.?[0-9]*)',
            r'([0-9,]+\.?[0-9]*)\s*\$',
        ]
        
        for i, pattern in enumerate(price_patterns):
            matches = list(re.finditer(pattern, automobile_text))
            print(f"\nPrice Pattern {i+1}: {pattern}")
            print(f"Found {len(matches)} matches:")
            for match in matches[:5]:  # Show first 5 matches
                print(f"  Match: '{match.group()}' at position {match.start()}")
                if match.groups():
                    print(f"    Groups: {match.groups()}")
        
        # Look for checkbox patterns
        checkbox_patterns = [
            r'Yes\s*No',
            r'New\?\s*Used\?',
            r'Owned\?\s*Leased\?',
            r'Gas\s*Diesel',
        ]
        
        for i, pattern in enumerate(checkbox_patterns):
            matches = list(re.finditer(pattern, automobile_text, re.IGNORECASE))
            print(f"\nCheckbox Pattern {i+1}: {pattern}")
            print(f"Found {len(matches)} matches:")
            for match in matches[:5]:  # Show first 5 matches
                print(f"  Match: '{match.group()}' at position {match.start()}")
        
        # Look for the actual vehicle data in the table
        print("\n" + "="*80)
        print("LOOKING FOR ACTUAL VEHICLE DATA IN TABLE:")
        print("="*80)
        
        # Search for the specific vehicle mentioned in the error
        search_terms = ["2012", "HONDA", "CIVIC", "M06911427865917"]
        for term in search_terms:
            if term in text:
                print(f"Found '{term}' in full text")
                # Find the context around this term
                term_pos = text.find(term)
                start_context = max(0, term_pos - 100)
                end_context = min(len(text), term_pos + 100)
                context = text[start_context:end_context]
                print(f"Context around '{term}':")
                print(f"  ...{context}...")
            else:
                print(f"'{term}' NOT found in full text")
        
    else:
        print("'Described Automobile' section not found")

if __name__ == "__main__":
    pdf_path = "../pdf_samples/FW_ NNS LTD_NNSLTD0-01_Auto_CAA(Future)_Eff Aug15/Autoappnotsigned - Signed-REVISED.pdf"
    debug_vehicle_extraction(pdf_path)
