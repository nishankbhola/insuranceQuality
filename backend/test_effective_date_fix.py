#!/usr/bin/env python3
"""
Test the fixed effective date validation
"""

import requests
import json
import os

def test_effective_date_fix():
    """Test that the effective date validation now passes"""
    print("Testing fixed effective date validation")
    print("=" * 50)

    # Check if the application PDF exists
    pdf_path = "../pdf_samples/nancy/Resubmission- AutoApp-Signed_ready_for_QC.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return

    print(f"✅ PDF file found: {os.path.basename(pdf_path)}")
    print()

    # Test the endpoint
    url = "http://localhost:5000/api/application-qc-existing-quote"

    try:
        with open(pdf_path, 'rb') as f:
            files = {'application': f}
            print("Sending request to endpoint...")
            response = requests.post(url, files=files)

        if response.status_code == 200:
            print("✅ Request successful!")
            result = response.json()

            print(f"\nResponse Summary:")
            print(f"  Total Checks: {result['summary']['total_checks']}")
            print(f"  Passed Checks: {result['summary']['passed_checks']}")
            print(f"  Failed Checks: {result['summary']['failed_checks']}")
            print(f"  Overall Status: {result['summary']['overall_status']}")

            # Check the effective date validation specifically
            print(f"\nEffective Date Validation:")
            failed_checks = result['qc_results']['failed_checks']
            effective_date_check = None
            
            for check in failed_checks:
                if "effective date" in check['check_description'].lower():
                    effective_date_check = check
                    break
            
            if effective_date_check:
                print(f"  ❌ FAIL: {effective_date_check['remarks']}")
            else:
                print("  ✅ PASS: Effective dates match - validation is now working correctly!")
                
            # Show all failed checks for context
            if failed_checks:
                print(f"\nAll Failed Checks:")
                for check in failed_checks:
                    print(f"  ❌ {check['check_description']}: {check['status']}")
                    print(f"     → {check['remarks']}")

        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running.")
        print("   Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_effective_date_fix()
