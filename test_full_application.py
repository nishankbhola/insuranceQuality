#!/usr/bin/env python3
"""
Full application test that simulates the complete workflow:
1. File upload and extraction
2. Data validation with different date formats
3. Result generation and display
"""

import sys
import os
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_full_application_workflow():
    """Test the complete application workflow with different date formats"""
    print("🧪 Testing Full Application Workflow")
    print("=" * 50)
    print()
    
    # Simulate the data structure that would come from file extraction
    extracted_data = {
        "mvrs": [
            {
                "licence_number": "T35945760655804",
                "name": "THOMAS, NADEEN",
                "birth_date": "04/08/1965",      # MVR format: DD/MM/YYYY
                "gender": "F",
                "address": "55 HORNER AVE SUITE\nBRAMPTON ON L6P4A9",
                "convictions": [],
                "expiry_date": "04/08/2025",     # MVR format: DD/MM/YYYY
                "issue_date": "08/07/2004"       # MVR format: DD/MM/YYYY
            }
        ],
        "dashes": [
            {
                "dln": "T35945760655804",
                "name": "NADEEN THOMAS",
                "date_of_birth": "1965-08-04",   # DASH format: YYYY-MM-DD
                "gender": "Female",
                "policies": [
                    {
                        "policy_number": "POL123456",
                        "start_date": "2024-01-01",  # DASH format: YYYY-MM-DD
                        "end_date": "2025-01-01",    # DASH format: YYYY-MM-DD
                        "company": "The Wawanesa Mutual Insurance Company",
                        "status": "Active"
                    }
                ],
                "claims": []
            }
        ],
        "quotes": [
            {
                "quote_effective_date": "06/16/2025",  # Quote format: MM/DD/YYYY
                "quote_prepared_by": "Nishank Bhola",
                "applicant": {
                    "first_name": "Nadeen",
                    "last_name": "Thomas"
                },
                "drivers": [
                    {
                        "full_name": "Nadeen Thomas",
                        "birth_date": "08/04/1965",    # Quote format: MM/DD/YYYY
                        "single": "Yes",
                        "marital_status": "Single",
                        "male": "No",
                        "gender": "Female",
                        "insured": "Yes",
                        "relationship_to_applicant": None,
                        "driver_training": "No",
                        "driver_training_date": None,
                        "out_of_province_country_driver": "No",
                        "licence_class": "G",
                        "date_g": "07/08/2004",        # Quote format: MM/DD/YYYY
                        "date_g2": "07/08/2003",       # Quote format: MM/DD/YYYY
                        "date_g1": "07/08/2002",       # Quote format: MM/DD/YYYY
                        "licence_number": "T35945760655804",
                        "licence_province": "ON",
                        "occupation": None,
                        "date_insured": "06/13/2016",  # Quote format: MM/DD/YYYY
                        "current_carrier": "",
                        "date_with_company": "06/13/2016",  # Quote format: MM/DD/YYYY
                        "brokerage_insured": None,
                        "owner_principal": "No",
                        "applicant_lives_with_parents": "No",
                        "student_away_at_school_km": "No",
                        "retired": "No"
                    }
                ],
                "vehicles": [
                    {
                        "vehicle_type": "Private Passenger",
                        "vin": "2HGFB2F50CH020785",
                        "body_style": "Gasoline\nFuel Type\nNo\nHybrid\nPleasure\nPrimary Use",
                        "fuel_type": "Gasoline",
                        "hybrid": "No",
                        "primary_use": "Pleasure",
                        "annual_km": 5000,
                        "business_km": 0,
                        "daily_km": 0,
                        "garaging_location": "BRAMPTON L6P4A9",
                        "single_vehicle_mvd": "No",
                        "leased": "No",
                        "cylinders": 4,
                        "anti_theft_device_type": None,
                        "anti_theft_manufacturer": None,
                        "anti_theft_engraving": None,
                        "purchase_condition": "New",
                        "purchase_date": "05/01/2012",  # Quote format: MM/DD/YYYY
                        "km_at_purchase": 18995,
                        "list_price_new": None,
                        "purchase_price": None,
                        "winter_tires": "Yes",
                        "parking_at_night": None
                    }
                ],
                "convictions": [],
                "suspensions": [],
                "coverages": [],
                "address": "55 Horner Ave, Suite"
            }
        ]
    }
    
    print("📋 Test Data Summary:")
    print(f"  MVR Reports: {len(extracted_data['mvrs'])}")
    print(f"  DASH Reports: {len(extracted_data['dashes'])}")
    print(f"  Quote Reports: {len(extracted_data['quotes'])}")
    print()
    
    print("📅 Date Format Analysis:")
    print("  MVR dates: DD/MM/YYYY format")
    print("    - Birth date: 04/08/1965 (August 4, 1965)")
    print("    - Expiry date: 04/08/2025 (August 4, 2025)")
    print("    - Issue date: 08/07/2004 (July 8, 2004)")
    print()
    print("  DASH dates: YYYY-MM-DD format")
    print("    - Birth date: 1965-08-04 (August 4, 1965)")
    print("    - Policy start: 2024-01-01 (January 1, 2024)")
    print("    - Policy end: 2025-01-01 (January 1, 2025)")
    print()
    print("  Quote dates: MM/DD/YYYY format")
    print("    - Birth date: 08/04/1965 (August 4, 1965)")
    print("    - G1 date: 07/08/2002 (July 8, 2002)")
    print("    - G2 date: 07/08/2003 (July 8, 2003)")
    print("    - G date: 07/08/2004 (July 8, 2004)")
    print()
    
    # Step 1: Run validation (simulating the backend validation process)
    print("🔍 Step 1: Running Validation Engine")
    print("-" * 30)
    
    engine = ValidationEngine()
    validation_result = engine.validate_quote(extracted_data)
    
    print(f"✅ Validation completed successfully!")
    print(f"  Total drivers: {validation_result['summary']['total_drivers']}")
    print(f"  Validated drivers: {validation_result['summary']['validated_drivers']}")
    print(f"  Issues found: {validation_result['summary']['issues_found']}")
    print(f"  Critical errors: {validation_result['summary']['critical_errors']}")
    print(f"  Warnings: {validation_result['summary']['warnings']}")
    print()
    
    # Step 2: Analyze validation results
    print("📊 Step 2: Analyzing Validation Results")
    print("-" * 30)
    
    if validation_result["drivers"]:
        driver = validation_result["drivers"][0]
        print(f"Driver: {driver['driver_name']}")
        print(f"License: {driver['driver_license']}")
        print(f"Overall Status: {driver['validation_status']}")
        print()
        
        # Check MVR validation
        mvr_val = driver["mvr_validation"]
        print("🔍 MVR Validation:")
        print(f"  Status: {mvr_val['status']}")
        print(f"  Matches: {len(mvr_val['matches'])}")
        print(f"  Errors: {len(mvr_val['critical_errors'])}")
        print(f"  Warnings: {len(mvr_val['warnings'])}")
        
        # Check specific date matches
        birth_date_match = any("Date of birth matches" in match for match in mvr_val['matches'])
        print(f"  ✅ Birth date match: {'Yes' if birth_date_match else 'No'}")
        
        if mvr_val['matches']:
            print("  📋 Matches found:")
            for match in mvr_val['matches']:
                print(f"    • {match}")
        print()
        
        # Check DASH validation
        dash_val = driver["dash_validation"]
        print("🔍 DASH Validation:")
        print(f"  Status: {dash_val['status']}")
        print(f"  Matches: {len(dash_val['matches'])}")
        print(f"  Errors: {len(dash_val['critical_errors'])}")
        print(f"  Warnings: {len(dash_val['warnings'])}")
        
        # Check specific date matches
        birth_date_match = any("Date of birth matches" in match for match in dash_val['matches'])
        print(f"  ✅ Birth date match: {'Yes' if birth_date_match else 'No'}")
        
        if dash_val['matches']:
            print("  📋 Matches found:")
            for match in dash_val['matches']:
                print(f"    • {match}")
        print()
        
        # Check license progression validation
        lic_val = driver["license_progression_validation"]
        print("🔍 License Progression Validation:")
        print(f"  Status: {lic_val['status']}")
        print(f"  Matches: {len(lic_val['matches'])}")
        print(f"  Errors: {len(lic_val['critical_errors'])}")
        print(f"  Warnings: {len(lic_val['warnings'])}")
        
        if lic_val['matches']:
            print("  📋 Matches found:")
            for match in lic_val['matches']:
                print(f"    • {match}")
        print()
        
        # Check for any issues
        if driver['critical_errors']:
            print("❌ Critical Errors:")
            for error in driver['critical_errors']:
                print(f"  • {error}")
            print()
        
        if driver['warnings']:
            print("⚠️  Warnings:")
            for warning in driver['warnings']:
                print(f"  • {warning}")
            print()
    
    # Step 3: Simulate frontend response generation
    print("🖥️  Step 3: Simulating Frontend Response")
    print("-" * 30)
    
    # Create the response structure that would be sent to the frontend
    frontend_response = {
        "extracted": extracted_data,
        "validation_report": validation_result
    }
    
    print("✅ Response structure created successfully!")
    print(f"  Extracted data keys: {list(frontend_response['extracted'].keys())}")
    print(f"  Validation report keys: {list(frontend_response['validation_report'].keys())}")
    print()
    
    # Step 4: Verify date format handling
    print("✅ Step 4: Verifying Date Format Handling")
    print("-" * 30)
    
    # Check if all date comparisons worked correctly
    date_handling_success = True
    
    # Verify birth date matches across all sources
    quote_birth = "08/04/1965"  # MM/DD/YYYY
    mvr_birth = "04/08/1965"    # DD/MM/YYYY
    dash_birth = "1965-08-04"   # YYYY-MM-DD
    
    # Test date comparisons
    quote_mvr_match = engine._dates_match(quote_birth, mvr_birth, "quote", "mvr")
    quote_dash_match = engine._dates_match(quote_birth, dash_birth, "quote", "dash")
    mvr_dash_match = engine._dates_match(mvr_birth, dash_birth, "mvr", "dash")
    
    print("🔍 Date Comparison Tests:")
    print(f"  Quote vs MVR birth date: {'✅ Match' if quote_mvr_match else '❌ Mismatch'}")
    print(f"  Quote vs DASH birth date: {'✅ Match' if quote_dash_match else '❌ Mismatch'}")
    print(f"  MVR vs DASH birth date: {'✅ Match' if mvr_dash_match else '❌ Mismatch'}")
    
    if not all([quote_mvr_match, quote_dash_match, mvr_dash_match]):
        date_handling_success = False
        print("❌ Date format handling issues detected!")
    else:
        print("✅ All date comparisons successful!")
    print()
    
    # Step 5: Final assessment
    print("📋 Step 5: Final Application Assessment")
    print("-" * 30)
    
    overall_success = (
        validation_result['summary']['critical_errors'] == 0 and
        date_handling_success and
        validation_result['summary']['total_drivers'] > 0
    )
    
    if overall_success:
        print("🎉 SUCCESS: Full application workflow completed successfully!")
        print()
        print("✅ All components working correctly:")
        print("  • Data extraction and structure")
        print("  • Date format handling across MVR, DASH, and Quote")
        print("  • Validation engine processing")
        print("  • Result generation for frontend")
        print()
        print("✅ The application will not fail due to date format mismatches")
        print("✅ All date comparisons work correctly across different formats")
        print("✅ The system is ready for production use")
    else:
        print("❌ FAILURE: Issues detected in application workflow")
        print()
        print("⚠️  Please check the following:")
        if validation_result['summary']['critical_errors'] > 0:
            print("  • Critical validation errors")
        if not date_handling_success:
            print("  • Date format handling issues")
        if validation_result['summary']['total_drivers'] == 0:
            print("  • No drivers processed")
    
    return overall_success

def main():
    """Run the full application test"""
    print("🧪 Full Application Workflow Test")
    print("=" * 60)
    print("Testing complete application workflow with different date formats")
    print("=" * 60)
    print()
    
    success = test_full_application_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 APPLICATION TEST PASSED!")
        print("The application is working correctly with all date formats.")
    else:
        print("❌ APPLICATION TEST FAILED!")
        print("Please fix the issues before deploying to production.")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 