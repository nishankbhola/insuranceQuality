#!/usr/bin/env python3
"""
Test script for the quote comparison functionality
"""

import requests
import os

def test_comparison_endpoint():
    """Test the /compare-quote endpoint"""
    
    # Test file path - use the Nancy PDF
    pdf_path = "../pdf_samples/nancy/Resubmission- AutoApp-Signed_ready_for_QC.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Test PDF not found: {pdf_path}")
        return
    
    print("Testing quote comparison endpoint...")
    
    # Prepare the file upload
    with open(pdf_path, 'rb') as f:
        files = {'file': ('test.pdf', f, 'application/pdf')}
        
        try:
            response = requests.post('http://127.0.0.1:8000/compare-quote', files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Comparison successful!")
                print(f"Summary: {result.get('summary', {})}")
                print(f"Drivers found: {len(result.get('drivers', []))}")
                print(f"Vehicles found: {len(result.get('vehicles', []))}")
                
                # Show detailed results
                if result.get('drivers'):
                    print("\nDriver Comparisons:")
                    for i, driver in enumerate(result['drivers']):
                        print(f"  {i+1}. {driver['json_driver']['full_name']} - {driver['status']}")
                
                if result.get('vehicles'):
                    print("\nVehicle Comparisons:")
                    for i, vehicle in enumerate(result['vehicles']):
                        print(f"  {i+1}. VIN: {vehicle['json_vehicle']['vin']} - {vehicle['status']}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure the Flask app is running on port 8000.")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_quote_data_loading():
    """Test that quote_result.json can be loaded"""
    try:
        from quote_comparison_service import QuoteComparisonService
        service = QuoteComparisonService()
        
        if service.quote_data:
            print("✅ Quote data loaded successfully")
            print(f"  Drivers: {len(service.quote_data.get('drivers', []))}")
            print(f"  Vehicles: {len(service.quote_data.get('vehicles', []))}")
        else:
            print("❌ No quote data found")
            
    except Exception as e:
        print(f"❌ Error loading quote data: {e}")

if __name__ == "__main__":
    print("=== Quote Comparison Test ===\n")
    
    # Test 1: Check if quote data loads
    test_quote_data_loading()
    print()
    
    # Test 2: Test the comparison endpoint
    test_comparison_endpoint() 