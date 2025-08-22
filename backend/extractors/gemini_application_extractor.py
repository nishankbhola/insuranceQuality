#!/usr/bin/env python3
"""
Gemini AI-based Application Extractor for QC Validation
Specialized for extracting and validating application data using Gemini AI
"""

import fitz  # PyMuPDF
import os
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiApplicationExtractor:
    """Gemini AI-based Application Extractor for QC validation"""
    
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create image_extracted folder if it doesn't exist
        self.images_folder = "image_extracted"
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
            print(f"Created folder: {self.images_folder}")
        
        # Required form strings for basic validation
        self.required_strings = [
            "COVERAGE NOT IN EFFECT",
            "Optional Accident Benefits Confirmation Form",
            "CONSENT TO RECEIVE ELECTRONIC COMMUNICATIONS",
            "PERSONAL INFORMATION CONSENT FORM",
            "PERSONAL INFORMATION CLIENT CONSENT FORM"
        ]
    
    def _cleanup_previous_images(self):
        """
        Clean up previous images in the image_extracted folder to save space
        """
        try:
            if os.path.exists(self.images_folder):
                # Get all files in the images folder
                files = os.listdir(self.images_folder)
                png_files = [f for f in files if f.lower().endswith('.png')]
                
                if png_files:
                    print(f"🧹 Cleaning up {len(png_files)} previous images from {self.images_folder}")
                    for file in png_files:
                        file_path = os.path.join(self.images_folder, file)
                        os.remove(file_path)
                    print(f"✓ Cleaned up {len(png_files)} old image files")
                else:
                    print(f"📁 No previous images found in {self.images_folder}")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up previous images: {e}")
    
    def extract_and_validate_application(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract application data and perform QC validation
        """
        print(f"Starting Gemini-based application extraction for: {os.path.basename(pdf_path)}")
        
        # Clean up previous images to save space
        self._cleanup_previous_images()
        
        result = {
            "extraction_info": {
                "original_file": os.path.basename(pdf_path),
                "extraction_method": "gemini_ai",
                "extraction_timestamp": datetime.now().isoformat()
            },
            "simple_validations": {},
            "gemini_validations": {},
            "gemini_response_raw": None,
            "api_usage": {
                "calls_made": 0,
                "daily_limit": 50,
                "remaining_calls": 50
            }
        }
        
        try:
            # Step 1: Simple string existence validations (no API cost)
            print("Running simple string validations...")
            result["simple_validations"] = self._perform_simple_validations(pdf_path)
            
            # Step 2: Extract the 3 required pages for Gemini analysis
            print("Extracting 3 pages for Gemini analysis...")
            extracted_pages_pdf = self._extract_required_pages(pdf_path)
            
            if not extracted_pages_pdf:
                print("Could not extract required pages")
                return result
            
            # Step 3: Send to Gemini for AI validation
            print("Sending to Gemini AI for validation...")
            gemini_response = self._validate_with_gemini(extracted_pages_pdf)
            
            if gemini_response:
                result["gemini_validations"] = gemini_response
                result["gemini_response_raw"] = gemini_response
                result["api_usage"]["calls_made"] = 1
                result["api_usage"]["remaining_calls"] = 49
                
                # Save gemini response to file
                self._save_gemini_response(gemini_response)
            
            # Clean up temporary file
            if os.path.exists(extracted_pages_pdf):
                os.remove(extracted_pages_pdf)
            
            print(f"Application QC extraction completed successfully")
            return result
            
        except Exception as e:
            print(f"Error in Gemini application extraction: {e}")
            # Clean up on error
            if 'extracted_pages_pdf' in locals() and os.path.exists(extracted_pages_pdf):
                os.remove(extracted_pages_pdf)
            raise e
    
    def _perform_simple_validations(self, pdf_path: str) -> Dict[str, Any]:
        """
        Perform simple string existence validations on the PDF
        """
        validations = {}
        
        try:
            # Extract all text from PDF
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()
            
            # Check for each required string
            for required_string in self.required_strings:
                found = required_string in full_text
                validations[self._clean_validation_key(required_string)] = {
                    "status": "pass" if found else "fail",
                    "description": f"Check if '{required_string}' exists in PDF",
                    "error_type": "critical" if not found else None
                }
            
            return validations
            
        except Exception as e:
            print(f"Error in simple validations: {e}")
            # Return failed validations for all if there's an error
            for required_string in self.required_strings:
                validations[self._clean_validation_key(required_string)] = {
                    "status": "fail",
                    "description": f"Check if '{required_string}' exists in PDF",
                    "error_type": "critical",
                    "error_message": f"Validation failed due to error: {str(e)}"
                }
            return validations
    
    def _clean_validation_key(self, text: str) -> str:
        """Convert validation description to clean key"""
        return text.lower().replace(" ", "_").replace("-", "_")
    
    def _extract_required_pages(self, pdf_path: str) -> Optional[str]:
        """
        Extract the 3 required pages and create a new PDF
        """
        try:
            doc = fitz.open(pdf_path)
            
            # Initialize page tracking
            ontario_app_page = None
            coverages_page = None
            remarks_page = None
            
            print(f"Scanning {len(doc)} pages for required content...")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().upper()
                
                # Page 1: Ontario Application for Automobile Insurance
                if ontario_app_page is None and "BROKER/AGENT BILL" in text:
                    ontario_app_page = page_num
                    print(f"✓ Found Ontario Application page: {page_num + 1}")
                
                # Page 2: Optional Additional Coverages/Endorsements
                if coverages_page is None and ("OPTIONAL ADDITIONAL COVERAGES" in text and "ENDORSEMENTS" in text):
                    coverages_page = page_num
                    print(f"✓ Found Optional Coverages/Endorsements page: {page_num + 1}")
                
                # Page 3: Remarks (look for specific underwriting questions)
                if remarks_page is None and "TOTAL NUMBER OF NON-LICENCED RESIDENTS" in text:
                    remarks_page = page_num
                    print(f"✓ Found Remarks page: {page_num + 1}")
            
            # Collect the found pages
            pages_to_extract = []
            page_descriptions = []
            
            if ontario_app_page is not None:
                pages_to_extract.append(ontario_app_page)
                page_descriptions.append(f"Ontario Application (page {ontario_app_page + 1})")
            
            if coverages_page is not None:
                pages_to_extract.append(coverages_page)
                page_descriptions.append(f"Optional Coverages (page {coverages_page + 1})")
            
            if remarks_page is not None:
                pages_to_extract.append(remarks_page)
                page_descriptions.append(f"Remarks (page {remarks_page + 1})")
            
            # Check if we found all required pages
            if len(pages_to_extract) != 3:
                print(f"⚠️  WARNING: Only found {len(pages_to_extract)}/3 required pages:")
                for desc in page_descriptions:
                    print(f"   - {desc}")
                
                missing_pages = []
                if ontario_app_page is None:
                    missing_pages.append("Ontario Application for Automobile Insurance")
                if coverages_page is None:
                    missing_pages.append("Optional Additional Coverages/Endorsements")
                if remarks_page is None:
                    missing_pages.append("Remarks")
                
                print(f"   Missing: {', '.join(missing_pages)}")
                print("   This may result in incomplete QC validation.")
                
                # If we don't have all pages, don't proceed with incomplete data
                if len(pages_to_extract) == 0:
                    print("❌ No required pages found. Cannot proceed with QC validation.")
                    doc.close()
                    return None
            
            print(f"📄 Extracting {len(pages_to_extract)} pages: {', '.join(page_descriptions)}")
            
            # Sort pages by page number to maintain order
            pages_to_extract.sort()
            
            # Create new PDF with extracted pages
            new_doc = fitz.open()
            for page_num in pages_to_extract:
                page = doc[page_num]
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            
            # Save temporary PDF
            temp_pdf_path = os.path.join(os.path.dirname(pdf_path), f"temp_qc_pages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            new_doc.save(temp_pdf_path)
            
            doc.close()
            new_doc.close()
            
            print(f"Extracted {len(pages_to_extract)} pages to: {temp_pdf_path}")
            return temp_pdf_path
            
        except Exception as e:
            print(f"Error extracting required pages: {e}")
            return None
    
    def _validate_with_gemini(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Send PDF to Gemini for AI-powered validation
        """
        try:
            # Convert PDF to images for Gemini
            doc = fitz.open(pdf_path)
            images = []
            
            # Create timestamp for this session
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            # Determine page types for better labeling
            page_labels = []
            temp_doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                # Get the actual page number from the extracted PDF
                original_page = doc[page_num]
                original_text = original_page.get_text().upper()
                
                # Determine page type
                if "BROKER/AGENT BILL" in original_text:
                    page_labels.append("ontario_application")
                elif "OPTIONAL ADDITIONAL COVERAGES" in original_text and "ENDORSEMENTS" in original_text:
                    page_labels.append("optional_coverages")
                elif "TOTAL NUMBER OF NON-LICENCED RESIDENTS" in original_text:
                    page_labels.append("remarks")
                else:
                    page_labels.append(f"page_{page_num + 1}")
            
            temp_doc.close()
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                images.append(img_data)
                
                # Save image to image_extracted folder with descriptive name
                page_label = page_labels[page_num] if page_num < len(page_labels) else f"page_{page_num + 1}"
                image_filename = f"{pdf_name}_{page_label}_{timestamp}.png"
                image_path = os.path.join(self.images_folder, image_filename)
                
                with open(image_path, 'wb') as img_file:
                    img_file.write(img_data)
                
                print(f"Saved extracted image: {image_path} ({page_label})")
            
            doc.close()
            
            if not images:
                print("No images extracted from PDF")
                return None
            
            print(f"Total {len(images)} images saved to {self.images_folder} folder")
            
            # Create the validation prompt
            prompt = self._create_gemini_prompt()
            
            # Prepare images for Gemini
            image_parts = []
            for i, img_data in enumerate(images):
                image_parts.append({
                    "mime_type": "image/png",
                    "data": img_data
                })
            
            # Send to Gemini
            print(f"Sending {len(images)} pages to Gemini for analysis...")
            response = self.model.generate_content([prompt] + image_parts)
            
            if not response or not response.text:
                print("No response from Gemini")
                return None
            
            # Parse JSON response
            try:
                # Clean the response text (remove markdown code blocks if present)
                response_text = response.text.strip()
                
                # Remove markdown code blocks if they exist
                if response_text.startswith("```json"):
                    response_text = response_text[7:]  # Remove ```json
                elif response_text.startswith("```"):
                    response_text = response_text[3:]  # Remove ```
                    
                if response_text.endswith("```"):
                    response_text = response_text[:-3]  # Remove closing ```
                
                response_text = response_text.strip()
                
                # Parse the cleaned JSON
                json_response = json.loads(response_text)
                print("Gemini validation completed successfully")
                return json_response
            except json.JSONDecodeError as e:
                print(f"Could not parse Gemini response as JSON: {e}")
                print(f"Raw response: {response.text}")
                print(f"Cleaned response: {response_text}")
                # Return a fallback structure
                return {
                    "error": "Could not parse Gemini response",
                    "raw_response": response.text
                }
            
        except Exception as e:
            print(f"Error in Gemini validation: {e}")
            return None
    
    def _create_gemini_prompt(self) -> str:
        """
        Create the comprehensive Gemini prompt for QC validation
        """
        return """You are an expert insurance application validator. Analyze these 3 pages from an Ontario automobile insurance application and perform the following validations. Return results in STRICT JSON format exactly as shown below.

VALIDATION REQUIREMENTS:

1. For each vehicle: If "Pleasure use" is not checked Fail test, else If "Pleasure use" is checked, verify "commuting one way = 0 kms" and "business use = 0%". Check remarks for justification, if remarks not justified for pleasure use, fail if justified pass.

2. For each vehicle: If business use % > 0, check if remarks exist explaining this, if remarks not justified for business use, fail if justified pass.

3. For each vehicle: Check if Purchase Date is present. if not present even for one vehcile fail else pass.

4. For each vehicle: Check if Purchase Price is present, if not present even for one vehcile fail else pass.

5. For each vehicle: Verify if New or Used is checked (not both, not neither).

6. For each vehicle: Verify if Owned or Leased is checked (not both, not neither).

7. Leased Vehicle Check: If any vehicle is marked as "Leased", then OPCF 5 ("Permission to Rent or Lease Automobiles and Extending") MUST be present on the Optional Coverages page. If NO vehicles are leased, this validation should PASS.

8. Compare  the number written infront of Total number of automobiles in the household or business.  vs. number of vehicles on policy. If total > number of vehicles on policy, check remarks for justification why there are more vehicles than the total number of automobiles in the household or business, if not justified fail, if justified pass.

9. If "Additional People in the Household That Are Licensed To Drive" is marked YES: Ensure there are remarks explaining this. if marked NO: pass the test

RETURN EXACTLY THIS JSON STRUCTURE (fill in pass/fail and details):

{
  "validation_1_pleasure_use": "pass/fail",
  "validation_2_business_use_remarks": "pass/fail", 
  "validation_3_purchase_date": "pass/fail",
  "validation_4_purchase_price": "pass/fail",
  "validation_5_new_used_status": "pass/fail",
  "validation_6_owned_leased_status": "pass/fail",
  "validation_7_lease_opcf5": "pass/fail",
  "validation_8_household_vehicle_count": "pass/fail",
  "validation_9_additional_drivers": "pass/fail",
  "details": {
    "failed_vehicles": [],
    "remarks_found": true/false,
    "total_vehicles_on_policy": 0,
    "total_vehicles_household": 0,
    "lease_vehicles_count": 0,
    "opcf5_found": true/false,
    "additional_drivers_marked": true/false,
    "validation_notes": "Brief explanation of any failures"
  }
}

VALIDATION LOGIC CLARIFICATIONS:
- For validation_7_lease_opcf5: PASS if no vehicles are leased OR if leased vehicles exist and OPCF5 is found. FAIL only if vehicles are leased but OPCF5 is missing.
- For validation_9_additional_drivers: PASS if additional drivers are NOT marked OR if they are marked and remarks explain this. FAIL only if additional drivers are marked YES but no remarks exist.

Be thorough and accurate. If you cannot determine something clearly, mark it as "fail" and explain in validation_notes."""
    
    def _save_gemini_response(self, response: Dict[str, Any]) -> None:
        """
        Save Gemini response to gemini_response.json
        """
        try:
            output_path = "gemini_response.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "response": response
                }, f, indent=2, ensure_ascii=False)
            print(f"Gemini response saved to: {output_path}")
        except Exception as e:
            print(f"Error saving Gemini response: {e}")


def extract_and_validate_application_qc(pdf_path: str) -> Dict[str, Any]:
    """
    Main function to extract and validate application using Gemini AI
    """
    extractor = GeminiApplicationExtractor()
    return extractor.extract_and_validate_application(pdf_path)
