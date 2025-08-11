#!/usr/bin/env python3
"""
Test script for the updated vehicle extraction logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractors.application_extractor import extract_vehicle_details

def test_vehicle_extraction():
    """Test the vehicle extraction with sample text"""
    
    # Sample text that matches the actual PDF format
    sample_text = """
    Purchased/Leased Year: 2020 Month: 2
    Purchase Price: $15,000
    New? No Used? Yes
    Owned? Yes Leased? No
    Estimated Annual Driving Distance: 6,000 km
    Type of Fuel Used: Gas Yes Diesel No
    """
    
    # Create a test vehicle
    test_vehicle = {
        "vehicle_number": 1,
        "year": "2020",
        "make": "HONDA",
        "model": "CIVIC",
        "vin": "TEST12345678901234"
    }
    
    print("Testing vehicle extraction...")
    print(f"Original vehicle: {test_vehicle}")
    print(f"Sample text: {sample_text}")
    
    # Extract details
    extract_vehicle_details(test_vehicle, sample_text)
    
    print(f"\nUpdated vehicle: {test_vehicle}")
    
    # Check if all required fields are populated
    required_fields = [
        "purchase_date",
        "purchase_price", 
        "purchase_condition",
        "owned",
        "leased",
        "annual_km",
        "fuel_type"
    ]
    
    print("\nField extraction results:")
    for field in required_fields:
        value = test_vehicle.get(field)
        status = "✓" if value is not None else "✗"
        print(f"  {field}: {status} {value}")
    
    # Count populated fields
    populated_count = sum(1 for field in required_fields if test_vehicle.get(field) is not None)
    print(f"\nTotal fields populated: {populated_count}/{len(required_fields)}")
    
    if populated_count == len(required_fields):
        print("✅ All required fields successfully extracted!")
    else:
        print("❌ Some fields are still missing")

if __name__ == "__main__":
    test_vehicle_extraction()
