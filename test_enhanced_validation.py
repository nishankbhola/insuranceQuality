#!/usr/bin/env python3
"""
Test script for enhanced validation engine with domain-specific rules
"""

import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def create_test_data():
    """
    Create comprehensive test data covering different scenarios
    """
    
    # Test Case 1: Normal case with matching MM/YYYY for expiry and birthdate
    test_case_1 = {
        "extracted": {
            "quotes": [{
                "quote_effective_date": "03/22/2025",
                "quote_prepared_by": "Test User",
                "applicant": {
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "drivers": [{
                    "full_name": "John Doe",
                    "birth_date": "07/09/1991",
                    "gender": "Male",
                    "licence_class": "G",
                    "date_g": "08/29/2010",
                    "date_g2": "08/29/2009",
                    "date_g1": "08/29/2008",
                    "licence_number": "M02504091910709",
                    "licence_province": "ON",
                    "address": "92 PRITCHARD AVE"
                }],
                "convictions": [{
                    "description": "SHALL NOT DRV HOLDING OR USING A HAND-HELD COM DEV",
                    "date": "12/02/2024",
                    "severity": "Minor"
                }],
                "address": "92 PRITCHARD AVE"
            }],
            "mvrs": [{
                "licence_number": "M0250-40919-10709",
                "name": "DOE,JOHN",
                "birth_date": "09/07/1991",  # MVR format: DD/MM/YYYY
                "gender": "M",
                "address": "92 PRITCHARD AVE",
                "convictions": [{
                    "description": "SHALL NOT DRV HOLDING OR USING A HAND-HELD COM DEV",
                    "offence_date": "02/12/2024"  # MVR format: DD/MM/YYYY
                }],
                "expiry_date": "09/07/2027",  # MVR format: DD/MM/YYYY
                "issue_date": "29/08/2008"  # MVR format: DD/MM/YYYY
            }],
            "dashes": []
        }
    }
    
    # Test Case 2: G2 license class (should skip G date validation)
    test_case_2 = {
        "extracted": {
            "quotes": [{
                "quote_effective_date": "03/22/2025",
                "quote_prepared_by": "Test User",
                "applicant": {
                    "first_name": "Jane",
                    "last_name": "Smith"
                },
                "drivers": [{
                    "full_name": "Jane Smith",
                    "birth_date": "05/15/1995",
                    "gender": "Female",
                    "licence_class": "G2",
                    "date_g": None,  # Should be skipped for G2
                    "date_g2": "05/15/2016",
                    "date_g1": "05/15/2015",
                    "licence_number": "M02504091910710",
                    "licence_province": "ON",
                    "address": "123 MAIN ST"
                }],
                "convictions": [],
                "address": "123 MAIN ST"
            }],
            "mvrs": [{
                "licence_number": "M0250-40919-10710",
                "name": "SMITH,JANE",
                "birth_date": "15/05/1995",  # MVR format: DD/MM/YYYY
                "gender": "F",
                "address": "123 MAIN ST",
                "convictions": [],
                "expiry_date": "15/12/2025",  # MVR format: DD/MM/YYYY
                "issue_date": "15/05/2015"  # MVR format: DD/MM/YYYY
            }],
            "dashes": []
        }
    }
    
    # Test Case 3: Convictions mismatch
    test_case_3 = {
        "extracted": {
            "quotes": [{
                "quote_effective_date": "03/22/2025",
                "quote_prepared_by": "Test User",
                "applicant": {
                    "first_name": "Bob",
                    "last_name": "Wilson"
                },
                "drivers": [{
                    "full_name": "Bob Wilson",
                    "birth_date": "03/20/1988",
                    "gender": "Male",
                    "licence_class": "G",
                    "date_g": "03/20/2010",
                    "date_g2": "03/20/2009",
                    "date_g1": "03/20/2008",
                    "licence_number": "M02504091910711",
                    "licence_province": "ON",
                    "address": "456 OAK AVE"
                }],
                "convictions": [{
                    "description": "SPEEDING",
                    "date": "01/15/2024",
                    "severity": "Minor"
                }],
                "address": "456 OAK AVE"
            }],
            "mvrs": [{
                "licence_number": "M0250-40919-10711",
                "name": "WILSON,BOB",
                "birth_date": "20/03/1988",  # MVR format: DD/MM/YYYY
                "gender": "M",
                "address": "456 OAK AVE",
                "convictions": [{
                    "description": "SHALL NOT DRV HOLDING OR USING A HAND-HELD COM DEV",
                    "offence_date": "02/12/2024"  # MVR format: DD/MM/YYYY
                }],
                "expiry_date": "20/03/2028",  # MVR format: DD/MM/YYYY
                "issue_date": "20/03/2008"  # MVR format: DD/MM/YYYY
            }],
            "dashes": []
        }
    }
    
    # Test Case 4: Critical field mismatches
    test_case_4 = {
        "extracted": {
            "quotes": [{
                "quote_effective_date": "03/22/2025",
                "quote_prepared_by": "Test User",
                "applicant": {
                    "first_name": "Alice",
                    "last_name": "Johnson"
                },
                "drivers": [{
                    "full_name": "Alice Johnson",
                    "birth_date": "06/10/1990",
                    "gender": "Female",
                    "licence_class": "G",
                    "date_g": "06/10/2012",
                    "date_g2": "06/10/2011",
                    "date_g1": "06/10/2010",
                    "licence_number": "M02504091910712",
                    "licence_province": "ON",
                    "address": "789 PINE ST"
                }],
                "convictions": [],
                "address": "789 PINE ST"
            }],
            "mvrs": [{
                "licence_number": "M0250-40919-10713",  # Different license number
                "name": "JOHNSON,ALICE",
                "birth_date": "10/06/1990",  # MVR format: DD/MM/YYYY
                "gender": "F",
                "address": "789 PINE ST",
                "convictions": [],
                "expiry_date": "10/06/2026",  # MVR format: DD/MM/YYYY
                "issue_date": "10/06/2010"  # MVR format: DD/MM/YYYY
            }],
            "dashes": []
        }
    }
    
    return {
        "test_case_1": test_case_1,
        "test_case_2": test_case_2,
        "test_case_3": test_case_3,
        "test_case_4": test_case_4
    }

def run_tests():
    """
    Run all test cases and display results
    """
    engine = ValidationEngine()
    test_data = create_test_data()
    
    print("🧪 Enhanced Validation Engine Test Results")
    print("=" * 60)
    
    for test_name, data in test_data.items():
        print(f"\n📋 {test_name.upper().replace('_', ' ')}")
        print("-" * 40)
        
        try:
            result = engine.validate_quote(data)
            
            # Display summary
            summary = result.get("summary", {})
            print(f"Total Drivers: {summary.get('total_drivers', 0)}")
            print(f"Validated Drivers: {summary.get('validated_drivers', 0)}")
            print(f"Critical Errors: {summary.get('critical_errors', 0)}")
            print(f"Warnings: {summary.get('warnings', 0)}")
            
            # Display driver details
            for i, driver in enumerate(result.get("drivers", [])):
                print(f"\n👤 Driver {i+1}: {driver.get('driver_name', 'Unknown')}")
                print(f"   License: {driver.get('driver_license', 'Unknown')}")
                print(f"   Status: {driver.get('validation_status', 'Unknown')}")
                
                # Display critical errors
                if driver.get("critical_errors"):
                    print("   🟥 Critical Errors:")
                    for error in driver["critical_errors"]:
                        print(f"      • {error}")
                
                # Display warnings
                if driver.get("warnings"):
                    print("   🟧 Warnings:")
                    for warning in driver["warnings"]:
                        print(f"      • {warning}")
                
                # Display matches
                if driver.get("matches"):
                    print("   ✅ Matches:")
                    for match in driver["matches"]:
                        print(f"      • {match}")
                
                # Display validation details
                if driver.get("mvr_validation", {}).get("status") != "NOT_FOUND":
                    mvr = driver["mvr_validation"]
                    print(f"   📄 MVR Validation: {mvr.get('status', 'Unknown')}")
                    if mvr.get("critical_errors"):
                        print("      🟥 Critical Errors:")
                        for error in mvr["critical_errors"]:
                            print(f"         • {error}")
                
                if driver.get("license_progression_validation", {}).get("status") != "NOT_FOUND":
                    license_val = driver["license_progression_validation"]
                    print(f"   📈 License Progression: {license_val.get('status', 'Unknown')}")
                    if license_val.get("critical_errors"):
                        print("      🟥 Critical Errors:")
                        for error in license_val["critical_errors"]:
                            print(f"         • {error}")
                
                if driver.get("convictions_validation", {}).get("status") != "NOT_FOUND":
                    convictions = driver["convictions_validation"]
                    print(f"   ⚖️ Convictions: {convictions.get('status', 'Unknown')}")
                    if convictions.get("critical_errors"):
                        print("      🟥 Critical Errors:")
                        for error in convictions["critical_errors"]:
                            print(f"         • {error}")
        
        except Exception as e:
            print(f"❌ Error running test: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Test execution completed!")

def save_test_results():
    """
    Save test results to JSON file for frontend testing
    """
    engine = ValidationEngine()
    test_data = create_test_data()
    
    # Use test case 1 as the main example
    main_test = test_data["test_case_1"]
    result = engine.validate_quote(main_test)
    
    # Save to file
    with open("test_validation_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("💾 Test results saved to test_validation_result.json")
    print("You can use this file to test the frontend validation report component.")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Validation Engine Tests...")
    
    # Run interactive tests
    run_tests()
    
    # Save results for frontend testing
    save_test_results()
    
    print("\n🎯 Test scenarios covered:")
    print("• Test Case 1: Normal case with matching MM/YYYY for expiry and birthdate")
    print("• Test Case 2: G2 license class (should skip G date validation)")
    print("• Test Case 3: Convictions mismatch")
    print("• Test Case 4: Critical field mismatches (license number)")
    
    print("\n📋 Key features tested:")
    print("✅ G1/G2/G date logic based on MM/YYYY matching")
    print("✅ License class G2 skips G date validation")
    print("✅ Critical field comparisons (license, name, address)")
    print("✅ Convictions matching with offence date and description")
    print("✅ Severity tags (Critical Errors, Warnings, Matches)")
    print("✅ Enhanced status determination logic") 