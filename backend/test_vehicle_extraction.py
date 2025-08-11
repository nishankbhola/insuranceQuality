#!/usr/bin/env python3
"""
Test script to verify vehicle extraction fix
"""
from extractors.application_extractor import extract_application_data
import os

def test_vehicle_extraction():
    """Test if vehicle extraction now correctly identifies only 1 vehicle"""
    
    pdf_path = '../pdf_samples/nancy/Resubmission- AutoApp-Signed_ready_for_QC.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    print("Testing vehicle extraction fix...")
    print(f"PDF: {pdf_path}")
    print("-" * 50)
    
    try:
        # Extract application data
        result = extract_application_data(pdf_path)
        
        # Check vehicle count
        vehicle_count = len(result.get("vehicles", []))
        print(f"Vehicles found: {vehicle_count}")
        
        if vehicle_count == 0:
            print("❌ No vehicles found - this might be an issue")
        elif vehicle_count == 1:
            print("✅ Correctly found 1 vehicle - this should fix the validation issue!")
        else:
            print(f"❌ Found {vehicle_count} vehicles - still too many")
        
        print("\nVehicle details:")
        for i, vehicle in enumerate(result.get("vehicles", [])):
            print(f"Vehicle {i+1}:")
            print(f"  Year: {vehicle.get('year', 'N/A')}")
            print(f"  Make: {vehicle.get('make', 'N/A')}")
            print(f"  Model: {vehicle.get('model', 'N/A')}")
            print(f"  VIN: {vehicle.get('vin', 'N/A')}")
            print(f"  Purchase Date: {vehicle.get('purchase_date', 'N/A')}")
            print(f"  Purchase Price: {vehicle.get('purchase_price', 'N/A')}")
            print(f"  Purchase Condition: {vehicle.get('purchase_condition', 'N/A')}")
            print(f"  Owned: {vehicle.get('owned', 'N/A')}")
            print(f"  Leased: {vehicle.get('leased', 'N/A')}")
            print(f"  Annual KM: {vehicle.get('annual_km', 'N/A')}")
            print(f"  Fuel Type: {vehicle.get('fuel_type', 'N/A')}")
            print()
        
        # Check if this would fix the validation issue
        if vehicle_count == 1:
            print("🎉 This should fix the validation issue!")
            print("The system will now only validate 1 vehicle instead of expecting 3.")
        else:
            print("⚠️  The validation issue may still persist.")
            
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vehicle_extraction()
