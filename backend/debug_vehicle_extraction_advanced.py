#!/usr/bin/env python3
"""
Advanced debug script to try different PDF extraction methods
"""
import fitz  # PyMuPDF
import re
import json

def debug_vehicle_extraction_advanced(pdf_path):
    """Try different PDF extraction methods to find vehicle data"""
    
    # Open PDF with PyMuPDF
    pdf_document = fitz.open(pdf_path)
    
    print(f"PDF has {len(pdf_document)} pages")
    
    # Method 1: Try to get text with different parameters
    print("\n=== Method 1: Text extraction with different parameters ===")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Try different text extraction methods
        text_normal = page.get_text()
        text_dict = page.get_text("dict")
        text_html = page.get_text("html")
        text_xml = page.get_text("xml")
        
        print(f"\nPage {page_num + 1}:")
        print(f"Normal text length: {len(text_normal)}")
        print(f"Dict text length: {len(str(text_dict))}")
        print(f"HTML text length: {len(text_html)}")
        print(f"XML text length: {len(text_xml)}")
        
        # Look for vehicle-related content in normal text
        if "HONDA" in text_normal or "CIVIC" in text_normal or "2012" in text_normal:
            print("Found vehicle info in normal text!")
            # Extract the relevant section
            lines = text_normal.split('\n')
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in ["HONDA", "CIVIC", "2012", "Vehicle", "Automobile"]):
                    print(f"Line {i}: {line}")
                    # Show surrounding context
                    start = max(0, i-5)
                    end = min(len(lines), i+6)
                    for j in range(start, end):
                        print(f"  {j}: {lines[j]}")
                    break
    
    # Method 2: Look for specific text blocks
    print("\n=== Method 2: Text block analysis ===")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Get text blocks
        blocks = page.get_text("dict")
        
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        if any(keyword in text for keyword in ["HONDA", "CIVIC", "2012", "Vehicle", "Automobile", "Purchase", "Price"]):
                            print(f"Page {page_num + 1}, Block: {text}")
                            print(f"  Font: {span.get('font', 'Unknown')}")
                            print(f"  Size: {span.get('size', 'Unknown')}")
                            print(f"  Color: {span.get('color', 'Unknown')}")
    
    # Method 3: Look for images that might contain form data
    print("\n=== Method 3: Image analysis ===")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Get image list
        image_list = page.get_images()
        if image_list:
            print(f"Page {page_num + 1} has {len(image_list)} images")
            for img_index, img in enumerate(image_list):
                print(f"  Image {img_index}: {img}")
    
    # Method 4: Check for form fields
    print("\n=== Method 4: Form field analysis ===")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Get form fields
        form_fields = page.get_text("dict")
        
        # Look for annotations
        annotations = list(page.annots())
        if annotations:
            print(f"Page {page_num + 1} has {len(annotations)} annotations")
            for annot in annotations:
                annot_type = annot.type[1] if annot.type else "Unknown"
                if annot_type == "FreeText":
                    content = annot.info.get("content", "")
                    if any(keyword in content for keyword in ["HONDA", "CIVIC", "2012", "Vehicle", "Automobile"]):
                        print(f"  Found vehicle info in annotation: {content}")
    
    pdf_document.close()

if __name__ == "__main__":
    pdf_path = "../pdf_samples/FW_ NNS LTD_NNSLTD0-01_Auto_CAA(Future)_Eff Aug15/Autoappnotsigned - Signed-REVISED.pdf"
    debug_vehicle_extraction_advanced(pdf_path)
