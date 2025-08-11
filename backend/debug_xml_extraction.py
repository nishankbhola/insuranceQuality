#!/usr/bin/env python3
"""
Debug script to extract XML content from specific pages to find vehicle data
"""
import fitz  # PyMuPDF
import re

def debug_xml_extraction(pdf_path):
    """Extract XML content from specific pages to find vehicle data"""
    
    # Open PDF with PyMuPDF
    pdf_document = fitz.open(pdf_path)
    
    # Focus on pages 5-7 where vehicle information should be
    target_pages = [4, 5, 6]  # 0-indexed
    
    for page_num in target_pages:
        if page_num < len(pdf_document):
            page = pdf_document.load_page(page_num)
            
            print(f"\n=== Page {page_num + 1} XML Content ===")
            
            # Get XML content
            xml_content = page.get_text("xml")
            
            # Look for vehicle-related content
            lines = xml_content.split('\n')
            
            # Find lines with vehicle information
            vehicle_keywords = ["HONDA", "CIVIC", "2012", "Vehicle", "Automobile", "Purchase", "Price", "VIN", "Serial"]
            
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in vehicle_keywords):
                    print(f"Line {i}: {line}")
                    # Show surrounding context
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    for j in range(start, end):
                        print(f"  {j}: {lines[j]}")
                    print()
            
            # Also look for any text that might contain vehicle data
            print(f"Total XML lines on page {page_num + 1}: {len(lines)}")
            
            # Look for specific patterns that might indicate filled form data
            for i, line in enumerate(lines):
                if "text" in line and ("2012" in line or "HONDA" in line or "CIVIC" in line):
                    print(f"Found potential vehicle data at line {i}: {line}")
    
    pdf_document.close()

if __name__ == "__main__":
    pdf_path = "../pdf_samples/FW_ NNS LTD_NNSLTD0-01_Auto_CAA(Future)_Eff Aug15/Autoappnotsigned - Signed-REVISED.pdf"
    debug_xml_extraction(pdf_path)
