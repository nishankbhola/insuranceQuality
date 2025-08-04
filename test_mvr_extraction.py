#!/usr/bin/env python3
"""
Test script to examine MVR PDF text extraction and debug the format
"""

import fitz  # PyMuPDF
import re
import json
import os

def test_mvr_extraction(pdf_path):
    """Test MVR extraction on a specific PDF file"""
    
    print(f"Testing MVR extraction on: {pdf_path}")
    
    # Open PDF with PyMuPDF
    pdf_document = fitz.open(pdf_path)
    text = ""
    
    # Extract text from all pages
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text()
        text += page_text
        print(f"Page {page_num + 1} length: {len(page_text)} characters")
    
    # Close the document
    pdf_document.close()
    
    # Save the raw text for inspection
    debug_filename = f"debug_mvr_{os.path.basename(pdf_path)}.txt"
    with open(debug_filename, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Raw text saved to: {debug_filename}")
    print(f"Total text length: {len(text)} characters")
    
    # Show first 500 characters
    print("\nFirst 500 characters of extracted text:")
    print("=" * 50)
    print(text[:500])
    print("=" * 50)
    
    # Try to find key patterns
    print("\nSearching for key patterns:")
    
    # Look for license number patterns
    license_patterns = [
        r'Licence Number:\s*([A-Z0-9\-]+)',
        r'License Number:\s*([A-Z0-9\-]+)',
        r'DLN:\s*([A-Z0-9\-]+)',
        r'Driver License:\s*([A-Z0-9\-]+)',
        r'([A-Z]\d{8,})',  # Generic pattern for license numbers
    ]
    
    for pattern in license_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"License pattern '{pattern}' found: {matches}")
    
    # Look for name patterns
    name_patterns = [
        r'Name:\s*([A-Z,\s]+)',
        r'Driver Name:\s*([A-Z,\s]+)',
        r'([A-Z]+\s*,\s*[A-Z]+)',  # LAST, FIRST format
    ]
    
    for pattern in name_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"Name pattern '{pattern}' found: {matches}")
    
    # Look for date patterns
    date_patterns = [
        r'Birth Date:\s*(\d{2}/\d{2}/\d{4})',
        r'Date of Birth:\s*(\d{2}/\d{2}/\d{4})',
        r'(\d{2}/\d{2}/\d{4})',  # Generic date pattern
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            print(f"Date pattern '{pattern}' found: {matches}")
    
    # Look for address patterns
    address_patterns = [
        r'Address:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n[A-Z][a-z]*\s*:|$)',
        r'Residence:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n[A-Z][a-z]*\s*:|$)',
    ]
    
    for pattern in address_patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f"Address pattern '{pattern}' found: {len(matches)} matches")
            for i, match in enumerate(matches[:2]):  # Show first 2
                print(f"  Address {i+1}: {match.strip()[:100]}...")
    
    return text

if __name__ == "__main__":
    # Test with one of the MVR files
    mvr_file = "pdf_samples/Paulo/MVRPrintAbstracts- Paulo Melo.pdf"
    
    if os.path.exists(mvr_file):
        test_mvr_extraction(mvr_file)
    else:
        print(f"File not found: {mvr_file}")
        print("Available files in pdf_samples/Paulo/:")
        for file in os.listdir("pdf_samples/Paulo/"):
            if "MVR" in file:
                print(f"  - {file}") 