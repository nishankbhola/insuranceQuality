"""
Test license number extraction from application PDF
"""
from extractors.application_extractor import extract_application_data
import json

def test_license_extraction():
    """Test license extraction from the actual PDF"""
    
    # Test with the RevisedAutoappUnsigned - Signed.pdf file
    pdf_path = "../pdf_samples/nadeen/RevisedAutoappUnsigned - Signed.pdf"
    
    print("Testing license extraction from application PDF...")
    
    try:
        # Extract application data
        application_data = extract_application_data(pdf_path)
        
        print("Extraction Results:")
        print("=" * 50)
        
        # Check applicant info
        applicant = application_data.get("applicant_info", {})
        print(f"Applicant Name: {applicant.get('full_name')}")
        print(f"License Number: {applicant.get('license_number')}")
        print(f"License Class: {applicant.get('license_class')}")
        print(f"Date of Birth: {applicant.get('date_of_birth')}")
        print()
        
        # Check drivers info
        drivers = application_data.get("drivers", [])
        print(f"Number of drivers found: {len(drivers)}")
        for i, driver in enumerate(drivers):
            print(f"Driver {i+1}:")
            print(f"  Name: {driver.get('name')}")
            print(f"  License Number: {driver.get('license_number')}")
            print(f"  Date of Birth: {driver.get('date_of_birth')}")
            print(f"  License Class: {driver.get('license_class')}")
        print()
        
        # Save the full results
        with open("license_test_results.json", "w", encoding="utf-8") as f:
            json.dump(application_data, f, indent=2, ensure_ascii=False)
        
        print("Full results saved to license_test_results.json")
        
        # Check if license was correctly extracted
        license_found = applicant.get('license_number') or (drivers and drivers[0].get('license_number'))
        if license_found:
            print(f"✅ License number extracted: {license_found}")
            if license_found == "T3594-57606-55804":
                print("✅ Correct license number format!")
            else:
                print(f"❌ Expected 'T3594-57606-55804', got '{license_found}'")
        else:
            print("❌ No license number found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_license_extraction()
