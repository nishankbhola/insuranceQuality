"""
Script to read the updated Excel file and update the QC checklist accordingly
"""
import pandas as pd
import json
from qc_checklist import QCChecker

def read_updated_checklist(filename="QC_Checklist_Review.xlsx"):
    """Read the updated Excel file and generate new QC checklist"""
    
    try:
        # Read the Excel file
        df = pd.read_excel(filename)
        
        print(f"📖 Reading updated checklist from: {filename}")
        print(f"📊 Found {len(df)} items")
        
        # Analyze the updates
        keep_items = df[df['Keep/Remove/Modify'].str.upper() == 'KEEP']
        modify_items = df[df['Keep/Remove/Modify'].str.upper() == 'MODIFY']
        remove_items = df[df['Keep/Remove/Modify'].str.upper() == 'REMOVE']
        review_items = df[df['Keep/Remove/Modify'].str.upper() == 'REVIEW']
        
        print(f"\n📋 Analysis of your updates:")
        print(f"   ✅ KEEP: {len(keep_items)} items")
        print(f"   🔄 MODIFY: {len(modify_items)} items")
        print(f"   ❌ REMOVE: {len(remove_items)} items")
        print(f"   ⏳ REVIEW: {len(review_items)} items (need your decision)")
        
        # Show items to be removed
        if len(remove_items) > 0:
            print(f"\n❌ Items marked for REMOVAL:")
            for _, item in remove_items.iterrows():
                print(f"   - {item['Checklist Item']} (Category: {item['Category']})")
                if pd.notna(item['Your Comments']) and item['Your Comments'].strip():
                    print(f"     Reason: {item['Your Comments']}")
        
        # Show items to be modified
        if len(modify_items) > 0:
            print(f"\n🔄 Items marked for MODIFICATION:")
            for _, item in modify_items.iterrows():
                print(f"   - {item['Checklist Item']} (Category: {item['Category']})")
                if pd.notna(item['Your Comments']) and item['Your Comments'].strip():
                    print(f"     Comments: {item['Your Comments']}")
                if pd.notna(item['New Logic (if different)']) and item['New Logic (if different)'].strip():
                    print(f"     New Logic: {item['New Logic (if different)']}")
        
        # Show items that still need review
        if len(review_items) > 0:
            print(f"\n⏳ Items still marked as REVIEW (need your decision):")
            for _, item in review_items.iterrows():
                print(f"   - {item['Checklist Item']} (Category: {item['Category']})")
        
        # Generate new checklist configuration
        new_checklist = []
        for _, item in df.iterrows():
            decision = str(item['Keep/Remove/Modify']).upper().strip()
            
            if decision in ['KEEP', 'MODIFY']:
                # Determine if it's required (Critical) or optional (Warning)
                is_required = 'Critical' in str(item['Current Status'])
                
                new_item = {
                    "id": item['ID'],
                    "category": item['Category'],
                    "name": item['Checklist Item'],
                    "required": is_required,
                    "current_logic": item['Current Logic'],
                    "application_data": item['Application Data Used'],
                    "quote_data": item['Quote Data Used'],
                    "your_comments": item['Your Comments'] if pd.notna(item['Your Comments']) else "",
                    "new_logic": item['New Logic (if different)'] if pd.notna(item['New Logic (if different)']) else ""
                }
                new_checklist.append(new_item)
        
        # Save the updated configuration
        config_filename = "updated_qc_checklist_config.json"
        with open(config_filename, 'w', encoding='utf-8') as f:
            json.dump({
                "checklist_items": new_checklist,
                "summary": {
                    "total_items": len(new_checklist),
                    "kept_items": len(keep_items),
                    "modified_items": len(modify_items),
                    "removed_items": len(remove_items),
                    "review_items": len(review_items)
                },
                "timestamp": pd.Timestamp.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Updated configuration saved to: {config_filename}")
        print(f"📊 New checklist will have {len(new_checklist)} items")
        
        return new_checklist, config_filename
        
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found.")
        print("Please make sure you have updated and saved the Excel file.")
        return None, None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None, None

def generate_updated_qc_code(checklist_items, output_file="updated_qc_checklist.py"):
    """Generate new QC checklist Python code based on updates"""
    
    code_template = '''"""
Updated QC Checklist Evaluation Module
Generated from user feedback in Excel file
"""
import json
from typing import Dict, List, Any
from datetime import datetime
import re

class UpdatedQCChecker:
    def __init__(self):
        self.checklist_items = [
'''
    
    # Add checklist items
    for item in checklist_items:
        code_template += f'''            {{"id": "{item['id']}", "category": "{item['category']}", "name": "{item['name']}", "required": {item['required']}}},\n'''
    
    code_template += '''        ]
    
    def evaluate_application_qc(self, application_data: Dict, quote_data: Dict) -> List[Dict]:
        """
        Evaluate application and quote data against updated QC checklist
        Returns list of QC results with status and remarks
        """
        results = []
        
        for item in self.checklist_items:
            result = {
                "checklist_item": item["name"],
                "category": item["category"],
                "status": "PASS",
                "remarks": "",
                "required": item["required"]
            }
            
            # TODO: Implement updated evaluation logic based on user feedback
            # Each item will need custom implementation based on the new logic provided
            
            results.append(result)
        
        return results
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code_template)
    
    print(f"📝 Generated updated QC code template: {output_file}")
    print("⚠️  Note: You'll need to implement the specific logic for each item")

if __name__ == "__main__":
    print("🔄 Reading your updated QC checklist...")
    checklist, config_file = read_updated_checklist()
    
    if checklist:
        print("\n🔧 Generating updated QC code template...")
        generate_updated_qc_code(checklist)
        
        print(f"\n✅ Update process complete!")
        print(f"📋 Review the updates above and the generated files:")
        print(f"   - {config_file}")
        print(f"   - updated_qc_checklist.py")
        print(f"\n💡 Next steps:")
        print(f"   1. Review the analysis above")
        print(f"   2. If everything looks correct, I can implement the changes")
        print(f"   3. The new logic will be applied to the QC checker")
    else:
        print("\n❌ Could not process the Excel file.")
        print("Please check the file and try again.")

