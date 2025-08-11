"""
Debug script to show vehicle count and data in application
"""
from qc_checklist import QCChecker

def debug_vehicle_data():
    """Debug vehicle data to understand why validation is failing"""
    
    # Sample application data that might match your real application
    application_data = {
        "application_info": {
            "application_date": "05/21/2025",
            "broker_name": "Test Broker"
        },
        "applicant_info": {
            "full_name": "Test Applicant",
            "date_of_birth": "01/01/1980",
            "gender": "F",
            "marital_status": "Single",
            "address": {
                "street": "123 Test Street",
                "city": "Toronto",
                "province": "ON",
                "postal_code": "M1M 1M1"
            },
            "license_number": "T1234-56789-01234",
            "license_class": "G"
        },
        "vehicles": [
            # Vehicle 1 - Has SOME automobile info
            {
                "year": "2020",
                "make": "HONDA",
                "model": "CIVIC",
                "vin": "2HGFB2F50CH020785",
                "purchase_date": "2020-02",  # ✅ Has purchase date
                "purchase_price": "15000.00",  # ✅ Has purchase price
                # ❌ Missing: purchase_condition, owned/leased, annual_km, fuel_type
            },
            # Vehicle 2 - Has NO automobile info
            {
                "year": "2017",
                "make": "HONDA", 
                "model": "CIVIC LX 4DR",
                "vin": "2HGFC2F58HH019274"
                # ❌ Missing: ALL automobile fields
            },
            # Vehicle 3 - Has NO automobile info
            {
                "year": "2012",
                "make": "HONDA",
                "model": "CIVIC LX 4DR", 
                "vin": "2HGFB2F50CH020785"
                # ❌ Missing: ALL automobile fields
            }
        ],
        "drivers": [
            {
                "name": "Test Applicant",
                "license_number": "T1234-56789-01234",
                "date_of_birth": "01/01/1980",
                "license_class": "G"
            }
        ],
        "coverage_info": {
            "accident_benefits": "Standard Coverage"
        },
        "policy_info": {
            "payment_frequency": "Company Bill",
            "effective_date": "08/19/2025"
        },
        "convictions": [],
        "claims_history": []
    }
    
    # Sample quote data
    quote_data = {
        "quote_effective_date": "08/19/2025",
        "drivers": [
            {
                "full_name": "Test Applicant",
                "licence_number": "T1234-56789-01234",
                "birth_date": "01/01/1980"
            }
        ],
        "vehicles": [
            {
                "primary_use": "Pleasure",
                "vin": "2HGFB2F50CH020785"
            }
        ],
        "convictions": [],
        "coverages": [
            {
                "type": "Third Party Liability",
                "limit": "1000000"
            }
        ]
    }
    
    print("VEHICLE DATA DEBUG:")
    print("=" * 50)
    print(f"Total vehicles detected: {len(application_data['vehicles'])}")
    print()
    
    # Show each vehicle's data
    for i, vehicle in enumerate(application_data['vehicles']):
        vehicle_num = i + 1
        print(f"VEHICLE {vehicle_num}:")
        print(f"  Year: {vehicle.get('year', 'MISSING')}")
        print(f"  Make: {vehicle.get('make', 'MISSING')}")
        print(f"  Model: {vehicle.get('model', 'MISSING')}")
        print(f"  VIN: {vehicle.get('vin', 'MISSING')}")
        print(f"  Purchase Date: {vehicle.get('purchase_date', '❌ MISSING')}")
        print(f"  Purchase Price: {vehicle.get('purchase_price', '❌ MISSING')}")
        print(f"  Purchase New/Used: {vehicle.get('purchase_condition', '❌ MISSING')}")
        print(f"  Owned: {vehicle.get('owned', '❌ MISSING')}")
        print(f"  Leased: {vehicle.get('leased', '❌ MISSING')}")
        print(f"  Annual KM: {vehicle.get('annual_km', '❌ MISSING')}")
        print(f"  Fuel Type: {vehicle.get('fuel_type', '❌ MISSING')}")
        print()
    
    print("=" * 50)
    print("WHY VALIDATION FAILS:")
    print("=" * 50)
    print("The system detects 3 vehicles but:")
    print("• Vehicle 1: Missing 4 automobile fields")
    print("• Vehicle 2: Missing ALL 6 automobile fields") 
    print("• Vehicle 3: Missing ALL 6 automobile fields")
    print()
    print("SOLUTION: Either fill in ALL automobile fields for ALL vehicles,")
    print("          OR remove vehicles that don't have complete information.")
    print()
    
    # Run QC to show the actual validation results
    qc_checker = QCChecker()
    results = qc_checker.evaluate_application_qc(application_data, quote_data)
    
    # Filter for automobile-related checks
    automobile_checks = [r for r in results if r["category"] == "Automobile Section"]
    
    print("AUTOMOBILE VALIDATION RESULTS:")
    print("=" * 40)
    for result in automobile_checks:
        status_symbol = "❌" if result["status"] == "FAIL" else "✅"
        print(f"{status_symbol} {result['check_description']}: {result['status']}")
        if result["remarks"]:
            print(f"    → {result['remarks']}")
        print()
    
    return results

if __name__ == "__main__":
    debug_vehicle_data()
