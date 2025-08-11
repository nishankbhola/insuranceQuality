#!/usr/bin/env python3
"""
Debug script to test purchase date extraction
"""
from extractors.application_extractor import extract_application_data
import os

def debug_purchase_date_extraction():
    """Debug purchase date extraction specifically"""
    
    pdf_path = '../pdf_samples/nancy/Resubmission- AutoApp-Signed_ready_for_QC.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    print("Debugging purchase date extraction...")
    print(f"PDF: {pdf_path}")
    print("-" * 50)
    
    try:
        # Extract application data
        result = extract_application_data(pdf_path)
        
        # Check vehicles
        vehicles = result.get("vehicles", [])
        print(f"Vehicles found: {len(vehicles)}")
        
        for i, vehicle in enumerate(vehicles):
            print(f"\nVehicle {i+1}:")
            print(f"  VIN: {vehicle.get('vin', 'N/A')}")
            print(f"  Purchase Date: {vehicle.get('purchase_date', 'N/A')}")
            print(f"  Purchase Price: {vehicle.get('purchase_price', 'N/A')}")
            
            # Print all vehicle keys to see what was extracted
            print(f"  All keys: {list(vehicle.keys())}")
            print(f"  All values: {vehicle}")
        
        # Check if the issue is in the extraction or validation
        print("\n" + "="*50)
        print("QC VALIDATION TEST:")
        print("="*50)
        
        # Import and test QC validation
        from qc_checklist import QCChecker
        
        # Create mock quote data for testing
        quote_data = {"quote_effective_date": "2025-05-02"}
        
        # Run QC validation
        qc_checker = QCChecker()
        qc_results = qc_checker.evaluate_application_qc(result, quote_data)
        
        # Find the purchase date validation result
        for result_item in qc_results:
            if "purchase_date" in result_item.get("check_description", "").lower():
                print(f"Purchase Date Check: {result_item['status']}")
                print(f"Remarks: {result_item['remarks']}")
                break
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_purchase_date_extraction()
