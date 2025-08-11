"""
Test script to demonstrate the vehicle extraction issue
Shows what data is currently being extracted vs what should be extracted
"""
from extractors.application_extractor import extract_application_data
import json

def test_vehicle_extraction_issue():
    """Test to show the current vehicle extraction problem"""
    
    # This would be the path to your actual PDF
    # For now, we'll simulate the data structure that should be extracted
    print("CURRENT ISSUE: Vehicle extraction is incomplete")
    print("=" * 60)
    
    # Based on the image description, here's what SHOULD be extracted:
    expected_data = {
        "vehicles": [
            {
                "year": "2015",
                "make": "HONDA", 
                "model": "CIVIC LX 4DR",
                "vin": "2HGFB2F44FH049170",
                "purchase_date": "2020-02",  # Purchased/Leased Year: 2020, Month: 2
                "purchase_price": "15000.00",  # $15,000.00
                "purchase_condition": "Used",  # "Used" is marked with X
                "owned": True,  # "Owned" is marked with X
                "leased": False,
                "annual_km": "6000",  # 6,000 km
                "fuel_type": "Gas"  # "Gas" is marked with X
            },
            {
                "year": None,  # Blank in form
                "make": None,   # Blank in form
                "model": None,  # Blank in form
                "vin": None,    # Blank in form
                "purchase_date": None,  # Blank in form
                "purchase_price": None,  # Blank in form
                "purchase_condition": None,  # Blank in form
                "owned": None,  # Blank in form
                "leased": None,  # Blank in form
                "annual_km": None,  # Blank in form
                "fuel_type": None  # Blank in form
            },
            {
                "year": None,  # Blank in form
                "make": None,   # Blank in form
                "model": None,  # Blank in form
                "vin": None,    # Blank in form
                "purchase_date": None,  # Blank in form
                "purchase_price": None,  # Blank in form
                "purchase_condition": None,  # Blank in form
                "owned": None,  # Blank in form
                "leased": None,  # Blank in form
                "annual_km": None,  # Blank in form
                "fuel_type": None  # Blank in form
            }
        ]
    }
    
    print("EXPECTED DATA STRUCTURE:")
    print(json.dumps(expected_data, indent=2))
    print()
    
    print("CURRENT PROBLEMS:")
    print("1. Vehicle 1: Missing purchase_condition, owned/leased, annual_km, fuel_type")
    print("2. Vehicle 2: Missing ALL automobile fields")
    print("3. Vehicle 3: Missing ALL automobile fields")
    print()
    
    print("WHY THIS HAPPENS:")
    print("- The extractor only processes the first automobile section")
    print("- It doesn't properly handle multiple vehicles")
    print("- The regex patterns may not match the exact format in the PDF")
    print()
    
    print("SOLUTION NEEDED:")
    print("- Fix the automobile section extraction to handle multiple vehicles")
    print("- Improve regex patterns to match the actual PDF format")
    print("- Ensure all 6 required automobile fields are extracted for each vehicle")
    print()
    
    print("REQUIRED FIELDS FOR EACH VEHICLE:")
    print("1. Purchase Date (purchase_date)")
    print("2. Purchase Price (purchase_price)")
    print("3. Purchase New or Used (purchase_condition)")
    print("4. Owned Or Leased (owned/leased)")
    print("5. Estimated Annual Driving Distance (annual_km)")
    print("6. Type of Fuel Used (fuel_type)")

if __name__ == "__main__":
    test_vehicle_extraction_issue()
