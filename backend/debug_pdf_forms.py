#!/usr/bin/env python3
"""
Debug script to check for form fields in the PDF
"""
import fitz  # PyMuPDF
import json

def debug_pdf_forms(pdf_path):
    """Debug PDF form fields"""
    
    # Open PDF with PyMuPDF
    pdf_document = fitz.open(pdf_path)
    
    print(f"PDF has {len(pdf_document)} pages")
    
    # Check each page for form fields
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Check for form fields
        form_fields = page.get_text("dict")
        
        # Look for annotations (which might contain form data)
        annotations = list(page.annots())
        if annotations:
            print(f"\nPage {page_num + 1} has {len(annotations)} annotations:")
            for annot in annotations:
                print(f"  Annotation type: {annot.type}")
                print(f"  Annotation content: {annot.get_text()}")
        
        # Look for widgets (form fields)
        widgets = list(page.widgets())
        if widgets:
            print(f"\nPage {page_num + 1} has {len(widgets)} widgets:")
            for widget in widgets:
                print(f"  Widget type: {widget.field_type}")
                print(f"  Widget name: {widget.field_name}")
                print(f"  Widget value: {widget.field_value}")
                print(f"  Widget text: {widget.text}")
        
        # Get text in different ways
        text_dict = page.get_text("dict")
        if "blocks" in text_dict:
            print(f"\nPage {page_num + 1} text blocks:")
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                text = span.get("text", "").strip()
                                if text and len(text) > 3:  # Only show meaningful text
                                    print(f"  Text: '{text}'")
        
        # Try to get text with different method
        text_raw = page.get_text("rawdict")
        if "blocks" in text_raw:
            print(f"\nPage {page_num + 1} raw text blocks:")
            for block in text_raw["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                text = span.get("text", "").strip()
                                if text and len(text) > 3:  # Only show meaningful text
                                    print(f"  Raw text: '{text}'")
    
    # Close the document
    pdf_document.close()

if __name__ == "__main__":
    pdf_path = "../pdf_samples/FW_ NNS LTD_NNSLTD0-01_Auto_CAA(Future)_Eff Aug15/Autoappnotsigned - Signed-REVISED.pdf"
    debug_pdf_forms(pdf_path)
