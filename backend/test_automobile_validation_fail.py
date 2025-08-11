"""
Test script for Automobile Validation FAIL scenarios
Shows how validation fails when automobile fields are missing
"""
from qc_checklist import QCChecker

def test_automobile_validation_fail():
    """Test automobile validation with missing vehicle data"""
    
    # Sample application data with MISSING automobile information
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
            {
                "year": "2020",
                "make": "HONDA",
                "model": "CIVIC",
                "vin": "2HGFB2F50CH020785"
                # Missing all required automobile fields:
                # - purchase_date
                # - purchase_price  
                # - purchase_condition
                # - owned/leased
                # - annual_km
                # - fuel_type
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
    
    # Initialize QC checker
    qc_checker = QCChecker()
    
    # Run QC evaluation
    results = qc_checker.evaluate_application_qc(application_data, quote_data)
    
    # Display results
    print("AUTOMOBILE VALIDATION FAIL TEST RESULTS:")
    print("=" * 60)
    
    # Filter for automobile-related checks
    automobile_checks = [r for r in results if r["category"] == "Automobile Section"]
    
    print(f"Total Checks: {len(results)}")
    print(f"Automobile Checks: {len(automobile_checks)}")
    print()
    
    print("AUTOMOBILE VALIDATION FAIL RESULTS:")
    print("=" * 40)
    for result in automobile_checks:
        status_symbol = "❌" if result["status"] == "FAIL" else "✅"
        print(f"{status_symbol} {result['check_description']}: {result['status']}")
        if result["remarks"]:
            print(f"    → {result['remarks']}")
    
    print()
    
    # Summary
    failed_automobile = [r for r in automobile_checks if r["status"] == "FAIL"]
    passed_automobile = [r for r in automobile_checks if r["status"] == "PASS"]
    
    print("AUTOMOBILE VALIDATION SUMMARY:")
    print("=" * 35)
    print(f"✅ Passed: {len(passed_automobile)}/6")
    print(f"❌ Failed: {len(failed_automobile)}/6")
    
    if failed_automobile:
        print(f"\n❌ Failed checks:")
        for check in failed_automobile:
            print(f"   • {check['check_description']}")
            print(f"     → {check['remarks']}")
    
    print("\n" + "="*60)
    print("EXPECTED BEHAVIOR:")
    print("All 6 automobile validations should FAIL because:")
    print("• Purchase Date is missing")
    print("• Purchase Price is missing") 
    print("• Purchase New or Used is missing")
    print("• Owned Or Leased is missing")
    print("• Estimated Annual Driving Distance is missing")
    print("• Type of Fuel Used is missing")
    
    return results

if __name__ == "__main__":
    test_automobile_validation_fail()
