"""
Test script for Application QC functionality
"""
from qc_checklist import QCChecker

def test_qc_functionality():
    """Test the QC checker with sample data"""
    
    # Sample application data
    application_data = {
        "application_info": {
            "application_date": "05/21/2025",
            "broker_name": "Test Broker"
        },
        "applicant_info": {
            "full_name": "Nadeen Thomas",
            "date_of_birth": "11/29/1984",
            "gender": "F",
            "marital_status": "Single",
            "address": {
                "street": "5 SEA DRIFTER CRES",
                "city": "BRAMPTON",
                "province": "ON",
                "postal_code": "L6P 4A9"
            },
            "license_number": "T3594-57606-55804",
            "license_class": "G"
        },
        "vehicles": [
            {
                "year": "2012",
                "make": "HONDA",
                "model": "CIVIC LX 4DR",
                "vin": "2HGFB2F50CH020785"
            }
        ],
        "drivers": [
            {
                "name": "Nadeen Thomas",
                "license_number": "T3594-57606-55804",
                "date_of_birth": "11/29/1984",
                "license_class": "G"
            }
        ],
        "coverage_info": {
            "accident_benefits": "Standard Coverage"
        },
        "policy_info": {
            "payment_frequency": "Company Bill",
            "effective_date": "06/16/2025"
        },
        "convictions": [],
        "claims_history": []
    }
    
    # Sample quote data
    quote_data = {
        "quote_effective_date": "08/19/2025",  # Different from app date - should trigger error
        "drivers": [
            {
                "full_name": "Nadeen Thomas",
                "licence_number": "T3594-57606-55804",
                "birth_date": "11/29/1984"
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
    print("QC Evaluation Results:")
    print("=" * 50)
    
    failed_checks = [r for r in results if r["status"] == "FAIL"]
    passed_checks = [r for r in results if r["status"] == "PASS"]
    
    print(f"Total Checks: {len(results)}")
    print(f"Failed Checks: {len(failed_checks)}")
    print(f"Passed Checks: {len(passed_checks)}")
    print()
    
    print("QC VALIDATION RESULTS:")
    print("=" * 50)
    
    for result in results:
        status_symbol = "❌" if result["status"] == "FAIL" else "✅"
        print(f"{status_symbol} {result['check_description']}: {result['status']}")
        if result["remarks"]:
            print(f"    → {result['remarks']}")
    
    print()
    print(f"Overall Status: {'FAIL' if failed_checks else 'PASS'}")
    
    return results

if __name__ == "__main__":
    test_qc_functionality()
