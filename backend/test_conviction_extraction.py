import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractors.application_extractor import extract_application_data
from extractors.quote_extractor import extract_quote_data

def test_conviction_extraction():
    """Test conviction extraction from both application and quote PDFs"""
    
    # Test with the actual PDFs
    app_path = "../pdf_samples/nadeen/RevisedAutoappUnsigned - Signed.pdf"
    quote_path = "../pdf_samples/nadeen/Nadeen_Auto Quote 2025-05-21.pdf"
    
    print("=== Testing Conviction Extraction ===")
    
    if os.path.exists(app_path):
        print(f"\n1. Extracting from Application: {app_path}")
        try:
            app_data = extract_application_data(app_path)
            print(f"   Raw convictions data: {app_data.get('convictions', [])}")
            
            # Count meaningful convictions
            meaningful_convictions = [c for c in app_data.get('convictions', []) 
                                   if c.get("description") and "No convictions" not in c.get("description", "")]
            print(f"   Meaningful convictions count: {len(meaningful_convictions)}")
            
            for i, conv in enumerate(meaningful_convictions):
                print(f"   Conviction {i+1}: {conv}")
                
        except Exception as e:
            print(f"   Error extracting application data: {e}")
    else:
        print(f"   Application PDF not found: {app_path}")
    
    if os.path.exists(quote_path):
        print(f"\n2. Extracting from Quote: {quote_path}")
        try:
            quote_data = extract_quote_data(quote_path)
            print(f"   Raw convictions data: {quote_data.get('convictions', [])}")
            
            # Count meaningful convictions
            meaningful_convictions = [c for c in quote_data.get('convictions', []) 
                                   if c.get("description")]
            print(f"   Meaningful convictions count: {len(meaningful_convictions)}")
            
            for i, conv in enumerate(meaningful_convictions):
                print(f"   Conviction {i+1}: {conv}")
                
        except Exception as e:
            print(f"   Error extracting quote data: {e}")
    else:
        print(f"   Quote PDF not found: {quote_path}")
    
    print("\n=== End of Test ===")

if __name__ == "__main__":
    test_conviction_extraction()
