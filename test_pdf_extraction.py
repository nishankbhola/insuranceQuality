#!/usr/bin/env python3
"""
Test different PDF text extraction methods to find one that works with MVR PDFs
"""

import fitz  # PyMuPDF
import os
import sys

def test_pdf_extraction_methods(pdf_path):
    """Test different PDF text extraction methods"""
    
    print(f"Testing PDF extraction methods on: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    # Open PDF
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)  # Test first page
    
    print(f"PDF has {len(pdf_document)} pages")
    
    # Method 1: Standard text extraction
    print("\nMethod 1: Standard text extraction")
    try:
        text1 = page.get_text()
        print(f"Length: {len(text1)} characters")
        print(f"First 200 chars: {repr(text1[:200])}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 2: Text extraction with "text" parameter
    print("\nMethod 2: Text extraction with 'text' parameter")
    try:
        text2 = page.get_text("text")
        print(f"Length: {len(text2)} characters")
        print(f"First 200 chars: {repr(text2[:200])}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 3: Extract text blocks
    print("\nMethod 3: Extract text blocks")
    try:
        blocks = page.get_text("dict")
        text3 = ""
        for block in blocks.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        text3 += span.get("text", "") + " "
        print(f"Length: {len(text3)} characters")
        print(f"First 200 chars: {repr(text3[:200])}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 4: Extract by words
    print("\nMethod 4: Extract by words")
    try:
        words = page.get_text("words")
        text4 = " ".join([word[4] for word in words if word[4]])
        print(f"Length: {len(text4)} characters")
        print(f"First 200 chars: {repr(text4[:200])}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 5: Extract by HTML and clean
    print("\nMethod 5: Extract by HTML")
    try:
        html_text = page.get_text("html")
        # Extract text from HTML
        import re
        text5 = re.sub(r'<[^>]+>', '', html_text)
        print(f"Length: {len(text5)} characters")
        print(f"First 200 chars: {repr(text5[:200])}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 6: Try with different encoding
    print("\nMethod 6: Try with different encoding")
    try:
        # Try to get text with different parameters
        text6 = page.get_text("text", sort=True)
        print(f"Length: {len(text6)} characters")
        print(f"First 200 chars: {repr(text6[:200])}")
    except Exception as e:
        print(f"Error: {e}")
    
    pdf_document.close()

if __name__ == "__main__":
    # Test with one of the MVR files
    mvr_file = "pdf_samples/Paulo/MVRPrintAbstracts- Paulo Melo.pdf"
    
    if os.path.exists(mvr_file):
        test_pdf_extraction_methods(mvr_file)
    else:
        print(f"File not found: {mvr_file}")
        print("Available files in pdf_samples/Paulo/:")
        for file in os.listdir("pdf_samples/Paulo/"):
            if "MVR" in file:
                print(f"  - {file}") 