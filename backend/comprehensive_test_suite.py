#!/usr/bin/env python3

import json
import os
from validator.compare_engine import ValidationEngine

def create_test_scenarios():
    """Create comprehensive test scenarios with fake data"""
    
    scenarios = {
        "perfect_match": {
            "description": "Perfect match scenario - all data aligns correctly",
            "quotes": [{
                "drivers": [{
                    "full_name": "John Smith",
                    "birth_date": "05/15/1990",
                    "licence_number": "A123456789012345",
                    "gender": "Male",
                    "date_insured": "2015-03-15",
                    "date_g1": "03/15/2015",
                    "date_g2": "03/15/2016",
                    "date_g": "03/15/2017",
                    "current_carrier": "ABC Insurance"
                }],
                "vehicles": [{
                    "garaging_location": "TORONTO M5V2H1"
                }],
                "claims": [{
                    "claim_type": "At-fault Collision",
                    "date": "2024-01-15",
                    "amount": "5000.00"
                }]
            }],
            "mvrs": [{
                "licence_number": "A123456789012345",
                "name": "SMITH,JOHN",
                "birth_date": "15/05/1990",
                "gender": "M",
                "address": "123 MAIN ST TORONTO ON M5V2H1",
                "expiry_date": "15/05/2025",
                "issue_date": "15/03/2015",
                "convictions": []
            }],
            "dashes": [{
                "dln": "A123456789012345",
                "name": "John Smith",
                "date_of_birth": "1990-05-15",
                "gender": "Male",
                "policies": [{
                    "policy_number": "1",
                    "start_date": "2015-03-15",
                    "end_date": "2016-03-15",
                    "company": "ABC Insurance",
                    "status": "Active"
                }],
                "claims": [{
                    "claim_number": "1",
                    "date": "2024-01-15",
                    "at_fault_percentage": 100,
                    "first_party_driver": "John Smith",
                    "total_loss": "5000.00",
                    "claim_status": "Closed"
                }]
            }]
        },
        
        "license_progression_mismatch": {
            "description": "License progression dates don't match calculated dates",
            "quotes": [{
                "drivers": [{
                    "full_name": "Jane Doe",
                    "birth_date": "10/20/1985",
                    "licence_number": "B987654321098765",
                    "gender": "Female",
                    "date_insured": "2010-06-20",
                    "date_g1": "06/20/2010",
                    "date_g2": "07/15/2011",  # Wrong date
                    "date_g": "08/10/2012",   # Wrong date
                    "current_carrier": "XYZ Insurance"
                }],
                "vehicles": [{
                    "garaging_location": "MISSISSAUGA L5B2C3"
                }],
                "claims": []
            }],
            "mvrs": [{
                "licence_number": "B987654321098765",
                "name": "DOE,JANE",
                "birth_date": "20/10/1985",
                "gender": "F",
                "address": "456 OAK AVE MISSISSAUGA ON L5B2C3",
                "expiry_date": "20/10/2030",
                "issue_date": "20/06/2010",
                "convictions": []
            }],
            "dashes": [{
                "dln": "B987654321098765",
                "name": "Jane Doe",
                "date_of_birth": "1985-10-20",
                "gender": "Female",
                "policies": [{
                    "policy_number": "1",
                    "start_date": "2010-06-20",
                    "end_date": "2011-06-20",
                    "company": "XYZ Insurance",
                    "status": "Active"
                }],
                "claims": []
            }]
        },
        
        "claims_validation_fail": {
            "description": "Claims validation fails - at-fault claim not in quote",
            "quotes": [{
                "drivers": [{
                    "full_name": "Bob Wilson",
                    "birth_date": "03/12/1988",
                    "licence_number": "C555666777888999",
                    "gender": "Male",
                    "date_insured": "2018-09-10",
                    "date_g1": "09/10/2018",
                    "date_g2": "09/10/2019",
                    "date_g": "09/10/2020",
                    "current_carrier": "DEF Insurance"
                }],
                "vehicles": [{
                    "garaging_location": "BRAMPTON L6T4M2"
                }],
                "claims": []  # No claims in quote
            }],
            "mvrs": [{
                "licence_number": "C555666777888999",
                "name": "WILSON,BOB",
                "birth_date": "12/03/1988",
                "gender": "M",
                "address": "789 PINE RD BRAMPTON ON L6T4M2",
                "expiry_date": "12/03/2033",
                "issue_date": "10/09/2018",
                "convictions": []
            }],
            "dashes": [{
                "dln": "C555666777888999",
                "name": "Bob Wilson",
                "date_of_birth": "1988-03-12",
                "gender": "Male",
                "policies": [{
                    "policy_number": "1",
                    "start_date": "2018-09-10",
                    "end_date": "2019-09-10",
                    "company": "DEF Insurance",
                    "status": "Active"
                }],
                "claims": [{
                    "claim_number": "1",
                    "date": "2023-05-20",
                    "at_fault_percentage": 100,
                    "first_party_driver": "Bob Wilson",
                    "total_loss": "8000.00",
                    "claim_status": "Closed"
                }]
            }]
        },
        
        "policy_date_mismatch": {
            "description": "Policy start date doesn't match date_insured",
            "quotes": [{
                "drivers": [{
                    "full_name": "Alice Brown",
                    "birth_date": "07/25/1992",
                    "licence_number": "D111222333444555",
                    "gender": "Female",
                    "date_insured": "2019-04-15",
                    "date_g1": "04/15/2019",
                    "date_g2": "04/15/2020",
                    "date_g": "04/15/2021",
                    "current_carrier": "GHI Insurance"
                }],
                "vehicles": [{
                    "garaging_location": "VAUGHAN L4K1N8"
                }],
                "claims": []
            }],
            "mvrs": [{
                "licence_number": "D111222333444555",
                "name": "BROWN,ALICE",
                "birth_date": "25/07/1992",
                "gender": "F",
                "address": "321 ELM ST VAUGHAN ON L4K1N8",
                "expiry_date": "25/07/2037",
                "issue_date": "15/04/2019",
                "convictions": []
            }],
            "dashes": [{
                "dln": "D111222333444555",
                "name": "Alice Brown",
                "date_of_birth": "1992-07-25",
                "gender": "Female",
                "policies": [{
                    "policy_number": "1",
                    "start_date": "2019-05-01",  # Different date
                    "end_date": "2020-05-01",
                    "company": "GHI Insurance",
                    "status": "Active"
                }],
                "claims": []
            }]
        },
        
        "multiple_drivers": {
            "description": "Multiple drivers scenario",
            "quotes": [{
                "drivers": [
                    {
                        "full_name": "Mike Johnson",
                        "birth_date": "12/08/1980",
                        "licence_number": "E777888999000111",
                        "gender": "Male",
                        "date_insured": "2012-11-08",
                        "date_g1": "11/08/2012",
                        "date_g2": "11/08/2013",
                        "date_g": "11/08/2014",
                        "current_carrier": "JKL Insurance"
                    },
                    {
                        "full_name": "Sarah Johnson",
                        "birth_date": "04/18/1982",
                        "licence_number": "F222333444555666",
                        "gender": "Female",
                        "date_insured": "2013-02-18",
                        "date_g1": "02/18/2013",
                        "date_g2": "02/18/2014",
                        "date_g": "02/18/2015",
                        "current_carrier": "JKL Insurance"
                    }
                ],
                "vehicles": [{
                    "garaging_location": "MARKHAM L3R5L6"
                }],
                "claims": []
            }],
            "mvrs": [
                {
                    "licence_number": "E777888999000111",
                    "name": "JOHNSON,MIKE",
                    "birth_date": "08/12/1980",
                    "gender": "M",
                    "address": "654 MAPLE AVE MARKHAM ON L3R5L6",
                    "expiry_date": "08/12/2035",
                    "issue_date": "08/11/2012",
                    "convictions": []
                },
                {
                    "licence_number": "F222333444555666",
                    "name": "JOHNSON,SARAH",
                    "birth_date": "18/04/1982",
                    "gender": "F",
                    "address": "654 MAPLE AVE MARKHAM ON L3R5L6",
                    "expiry_date": "18/04/2037",
                    "issue_date": "18/02/2013",
                    "convictions": []
                }
            ],
            "dashes": [
                {
                    "dln": "E777888999000111",
                    "name": "Mike Johnson",
                    "date_of_birth": "1980-12-08",
                    "gender": "Male",
                    "policies": [{
                        "policy_number": "1",
                        "start_date": "2012-11-08",
                        "end_date": "2013-11-08",
                        "company": "JKL Insurance",
                        "status": "Active"
                    }],
                    "claims": []
                },
                {
                    "dln": "F222333444555666",
                    "name": "Sarah Johnson",
                    "date_of_birth": "1982-04-18",
                    "gender": "Female",
                    "policies": [{
                        "policy_number": "1",
                        "start_date": "2013-02-18",
                        "end_date": "2014-02-18",
                        "company": "JKL Insurance",
                        "status": "Active"
                    }],
                    "claims": []
                }
            ]
        },
        
        "convictions_mismatch": {
            "description": "Convictions don't match between MVR and Quote",
            "quotes": [{
                "drivers": [{
                    "full_name": "Tom Davis",
                    "birth_date": "09/30/1987",
                    "licence_number": "G333444555666777",
                    "gender": "Male",
                    "date_insured": "2016-12-30",
                    "date_g1": "12/30/2016",
                    "date_g2": "12/30/2017",
                    "date_g": "12/30/2018",
                    "current_carrier": "MNO Insurance"
                }],
                "vehicles": [{
                    "garaging_location": "OAKVILLE L6J7W8"
                }],
                "convictions": [{
                    "description": "Speeding 60 km/h in 50 km/h zone",
                    "date": "2023-08-15"
                }],
                "claims": []
            }],
            "mvrs": [{
                "licence_number": "G333444555666777",
                "name": "DAVIS,TOM",
                "birth_date": "30/09/1987",
                "gender": "M",
                "address": "987 CEDAR BLVD OAKVILLE ON L6J7W8",
                "expiry_date": "30/09/2032",
                "issue_date": "30/12/2016",
                "convictions": [{
                    "description": "SPEEDING 70 KMH IN 50 KMH ZONE",
                    "offence_date": "15/08/2023"
                }]
            }],
            "dashes": [{
                "dln": "G333444555666777",
                "name": "Tom Davis",
                "date_of_birth": "1987-09-30",
                "gender": "Male",
                "policies": [{
                    "policy_number": "1",
                    "start_date": "2016-12-30",
                    "end_date": "2017-12-30",
                    "company": "MNO Insurance",
                    "status": "Active"
                }],
                "claims": []
            }]
        },
        
        "zero_at_fault_claims": {
            "description": "Claims with 0% at-fault should be skipped",
            "quotes": [{
                "drivers": [{
                    "full_name": "Lisa Chen",
                    "birth_date": "11/14/1995",
                    "licence_number": "H444555666777888",
                    "gender": "Female",
                    "date_insured": "2020-03-14",
                    "date_g1": "03/14/2020",
                    "date_g2": "03/14/2021",
                    "date_g": "03/14/2022",
                    "current_carrier": "PQR Insurance"
                }],
                "vehicles": [{
                    "garaging_location": "RICHMOND HILL L4C5K6"
                }],
                "claims": []
            }],
            "mvrs": [{
                "licence_number": "H444555666777888",
                "name": "CHEN,LISA",
                "birth_date": "14/11/1995",
                "gender": "F",
                "address": "147 BIRCH LN RICHMOND HILL ON L4C5K6",
                "expiry_date": "14/11/2040",
                "issue_date": "14/03/2020",
                "convictions": []
            }],
            "dashes": [{
                "dln": "H444555666777888",
                "name": "Lisa Chen",
                "date_of_birth": "1995-11-14",
                "gender": "Female",
                "policies": [{
                    "policy_number": "1",
                    "start_date": "2020-03-14",
                    "end_date": "2021-03-14",
                    "company": "PQR Insurance",
                    "status": "Active"
                }],
                "claims": [
                    {
                        "claim_number": "1",
                        "date": "2024-02-10",
                        "at_fault_percentage": 0,  # Should be skipped
                        "first_party_driver": "Lisa Chen",
                        "total_loss": "3000.00",
                        "claim_status": "Closed"
                    },
                    {
                        "claim_number": "2",
                        "date": "2024-03-20",
                        "at_fault_percentage": 100,  # Should be validated
                        "first_party_driver": "Lisa Chen",
                        "total_loss": "6000.00",
                        "claim_status": "Closed"
                    }
                ]
            }]
        }
    }
    
    return scenarios

def run_comprehensive_tests():
    """Run comprehensive tests on all scenarios"""
    
    print("🚀 COMPREHENSIVE APPLICATION TEST SUITE")
    print("=" * 60)
    
    scenarios = create_test_scenarios()
    engine = ValidationEngine()
    
    results = {}
    
    for scenario_name, scenario_data in scenarios.items():
        print(f"\n📋 Testing Scenario: {scenario_name}")
        print(f"Description: {scenario_data['description']}")
        print("-" * 50)
        
        # Prepare validation data
        validation_data = {
            "extracted": {
                "quotes": scenario_data["quotes"],
                "mvrs": scenario_data["mvrs"],
                "dashes": scenario_data["dashes"]
            }
        }
        
        # Run validation
        try:
            validation_result = engine.validate_quote(validation_data)
            
            # Analyze results
            total_drivers = validation_result['summary']['total_drivers']
            validated_drivers = validation_result['summary']['validated_drivers']
            critical_errors = validation_result['summary']['critical_errors']
            warnings = validation_result['summary']['warnings']
            
            overall_score = (validated_drivers / total_drivers * 100) if total_drivers > 0 else 0
            
            print(f"✅ Total Drivers: {total_drivers}")
            print(f"✅ Validated Drivers: {validated_drivers}")
            print(f"❌ Critical Errors: {critical_errors}")
            print(f"⚠️  Warnings: {warnings}")
            print(f"📊 Overall Score: {overall_score:.1f}%")
            
            # Detailed driver analysis
            for i, driver_result in enumerate(validation_result.get('drivers', [])):
                print(f"\n  Driver {i+1}: {driver_result.get('driver_name', 'Unknown')}")
                print(f"    Status: {driver_result.get('validation_status', 'Unknown')}")
                
                # MVR Validation
                mvr_validation = driver_result.get('mvr_validation', {})
                print(f"    MVR: {mvr_validation.get('status', 'Unknown')}")
                if mvr_validation.get('critical_errors'):
                    for error in mvr_validation['critical_errors'][:2]:  # Show first 2 errors
                        print(f"      ❌ {error}")
                
                # License Progression
                license_validation = driver_result.get('license_progression_validation', {})
                print(f"    License: {license_validation.get('status', 'Unknown')}")
                if license_validation.get('critical_errors'):
                    for error in license_validation['critical_errors'][:2]:
                        print(f"      ❌ {error}")
                
                # DASH Validation
                dash_validation = driver_result.get('dash_validation', {})
                print(f"    DASH: {dash_validation.get('status', 'Unknown')}")
                if dash_validation.get('critical_errors'):
                    for error in dash_validation['critical_errors'][:2]:
                        print(f"      ❌ {error}")
            
            results[scenario_name] = {
                "overall_score": overall_score,
                "status": "PASS" if overall_score >= 80 else "WARNING" if overall_score >= 50 else "FAIL",
                "critical_errors": critical_errors,
                "warnings": warnings,
                "validation_result": validation_result
            }
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results[scenario_name] = {
                "overall_score": 0,
                "status": "ERROR",
                "error": str(e)
            }
    
    # Summary Report
    print(f"\n📈 TEST SUMMARY REPORT")
    print("=" * 60)
    
    total_scenarios = len(scenarios)
    passed_scenarios = sum(1 for r in results.values() if r.get('status') == 'PASS')
    warning_scenarios = sum(1 for r in results.values() if r.get('status') == 'WARNING')
    failed_scenarios = sum(1 for r in results.values() if r.get('status') == 'FAIL')
    error_scenarios = sum(1 for r in results.values() if r.get('status') == 'ERROR')
    
    print(f"Total Scenarios: {total_scenarios}")
    print(f"✅ Passed: {passed_scenarios}")
    print(f"⚠️  Warnings: {warning_scenarios}")
    print(f"❌ Failed: {failed_scenarios}")
    print(f"💥 Errors: {error_scenarios}")
    
    overall_success_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
    print(f"\n🎯 Overall Success Rate: {overall_success_rate:.1f}%")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS")
    print("-" * 40)
    
    for scenario_name, result in results.items():
        status_icon = "✅" if result.get('status') == 'PASS' else "⚠️" if result.get('status') == 'WARNING' else "❌" if result.get('status') == 'FAIL' else "💥"
        print(f"{status_icon} {scenario_name}: {result.get('overall_score', 0):.1f}% ({result.get('status', 'Unknown')})")
    
    # Save detailed results
    with open("comprehensive_test_results.json", "w") as f:
        json.dump({
            "test_summary": {
                "total_scenarios": total_scenarios,
                "passed": passed_scenarios,
                "warnings": warning_scenarios,
                "failed": failed_scenarios,
                "errors": error_scenarios,
                "success_rate": overall_success_rate
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: comprehensive_test_results.json")
    
    return results

if __name__ == "__main__":
    run_comprehensive_tests() 