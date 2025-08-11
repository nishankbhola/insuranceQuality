"""
Test script for improved automobile extraction
Tests the enhanced extraction logic with sample data
"""
from extractors.application_extractor import extract_automobile_section_details
import json

def test_improved_extraction():
    """Test the improved automobile extraction logic"""
    
    # Sample text that mimics the PDF format from the image
    sample_text = """
    Automobile Section
    
    Automobile No. 1:
    Model Year: 2015
    Make or Trade Name: HONDA
    Model: CIVIC LX 4DR
    Body Type: Private Passenger-4 Door Sedan/Har
    No. of Cylinders or Engine Size: 4/0
    Gross Vehicle Weight Rating: Kg
    Vehicle Identification No. (Serial No.): 2HGFB2F44FH049170
    Owned? Leased? X Owned
    Purchased/Leased Year: 2020 Month: 2
    New? Used? X Used
    Purchase Price (including options & taxes): $15,000.00
    Automobile Use: X Pleasure
    Commute One-Way: 0 km
    Business Use %: 0 %
    Estimated Annual Driving Distance: 6,000 km
    Is any automobile used for car pooling?: No
    Type of fuel used: X Gas Diesel If other, give details:
    Unrepaired Damage?: No
    Modified/Customized (See Note 2): No
    
    Automobile No. 2:
    Model Year: 
    Make or Trade Name: 
    Model: 
    Body Type: 
    No. of Cylinders or Engine Size: 
    Gross Vehicle Weight Rating: 
    Vehicle Identification No. (Serial No.): 
    Owned? Leased? 
    Purchased/Leased Year:  Month: 
    New? Used? 
    Purchase Price (including options & taxes): 
    Automobile Use: 
    Commute One-Way:  km
    Business Use %:  %
    Estimated Annual Driving Distance:  km
    Is any automobile used for car pooling?: 
    Type of fuel used:  Gas Diesel If other, give details:
    Unrepaired Damage?: 
    Modified/Customized (See Note 2): 
    
    Automobile No. 3:
    Model Year: 
    Make or Trade Name: 
    Model: 
    Body Type: 
    No. of Cylinders or Engine Size: 
    Gross Vehicle Weight Rating: 
    Vehicle Identification No. (Serial No.): 
    Owned? Leased? 
    Purchased/Leased Year:  Month: 
    New? Used? 
    Purchase Price (including options & taxes): 
    Automobile Use: 
    Commute One-Way:  km
    Business Use %:  %
    Estimated Annual Driving Distance:  km
    Is any automobile used for car pooling?: 
    Type of fuel used:  Gas Diesel If other, give details:
    Unrepaired Damage?: 
    Modified/Customized (See Note 2): 
    """
    
    # Sample result structure with 3 vehicles
    result = {
        "vehicles": [
            {
                "year": "2015",
                "make": "HONDA",
                "model": "CIVIC LX 4DR",
                "vin": "2HGFB2F44FH049170"
            },
            {
                "year": None,
                "make": None,
                "model": None,
                "vin": None
            },
            {
                "year": None,
                "make": None,
                "model": None,
                "vin": None
            }
        ]
    }
    
    print("TESTING IMPROVED AUTOMOBILE EXTRACTION")
    print("=" * 50)
    print()
    
    print("BEFORE EXTRACTION:")
    for i, vehicle in enumerate(result["vehicles"]):
        print(f"Vehicle {i+1}:")
        print(f"  Purchase Date: {vehicle.get('purchase_date', 'MISSING')}")
        print(f"  Purchase Price: {vehicle.get('purchase_price', 'MISSING')}")
        print(f"  Purchase Condition: {vehicle.get('purchase_condition', 'MISSING')}")
        print(f"  Owned: {vehicle.get('owned', 'MISSING')}")
        print(f"  Leased: {vehicle.get('leased', 'MISSING')}")
        print(f"  Annual KM: {vehicle.get('annual_km', 'MISSING')}")
        print(f"  Fuel Type: {vehicle.get('fuel_type', 'MISSING')}")
        print()
    
    # Run the improved extraction
    extract_automobile_section_details(sample_text, result)
    
    print("AFTER EXTRACTION:")
    for i, vehicle in enumerate(result["vehicles"]):
        print(f"Vehicle {i+1}:")
        print(f"  Purchase Date: {vehicle.get('purchase_date', 'MISSING')}")
        print(f"  Purchase Price: {vehicle.get('purchase_price', 'MISSING')}")
        print(f"  Purchase Condition: {vehicle.get('purchase_condition', 'MISSING')}")
        print(f"  Owned: {vehicle.get('owned', 'MISSING')}")
        print(f"  Leased: {vehicle.get('leased', 'MISSING')}")
        print(f"  Annual KM: {vehicle.get('annual_km', 'MISSING')}")
        print(f"  Fuel Type: {vehicle.get('fuel_type', 'MISSING')}")
        print()
    
    print("EXPECTED RESULTS:")
    print("Vehicle 1: Should have all fields filled")
    print("Vehicle 2: Should have all fields as None (blank in form)")
    print("Vehicle 3: Should have all fields as None (blank in form)")
    print()
    
    # Check if extraction worked correctly
    vehicle1 = result["vehicles"][0]
    expected_fields = {
        "purchase_date": "2020-02",
        "purchase_price": "15,000.00",
        "purchase_condition": "Used",
        "owned": True,
        "leased": False,
        "annual_km": "6000",
        "fuel_type": "Gas"
    }
    
    print("VALIDATION RESULTS:")
    all_correct = True
    for field, expected_value in expected_fields.items():
        actual_value = vehicle1.get(field)
        if actual_value == expected_value:
            print(f"✅ {field}: {actual_value}")
        else:
            print(f"❌ {field}: Expected {expected_value}, Got {actual_value}")
            all_correct = False
    
    if all_correct:
        print("\n🎉 All fields extracted correctly!")
    else:
        print("\n⚠️  Some fields need adjustment")

if __name__ == "__main__":
    test_improved_extraction()
