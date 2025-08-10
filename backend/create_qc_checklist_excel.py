"""
Create Excel file with Application QC Checklist for review and modification
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

def create_qc_checklist_excel():
    """Create Excel file with current QC checklist"""
    
    # Current QC checklist data
    checklist_data = [
        # Signatures
        {
            "ID": "signed_application",
            "Category": "Signatures", 
            "Checklist Item": "Signed Application by Insured",
            "Current Logic": "Check if applicant name exists in application",
            "Application Data Used": "applicant_info.full_name",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "date_matches_effective",
            "Category": "Signatures",
            "Checklist Item": "Date App Signed matches Effective Date", 
            "Current Logic": "Compare application date vs quote effective date (exact match)",
            "Application Data Used": "application_info.application_date",
            "Quote Data Used": "quote_effective_date",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "signed_by_all_drivers",
            "Category": "Signatures",
            "Checklist Item": "Signed by all drivers on policy",
            "Current Logic": "Check if all drivers have names/signatures",
            "Application Data Used": "drivers[].name",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        
        # Completed Information
        {
            "ID": "complete_personal_info",
            "Category": "Completed Information",
            "Checklist Item": "Complete Personal Information",
            "Current Logic": "Check required fields: full_name, date_of_birth, gender, marital_status",
            "Application Data Used": "applicant_info.{full_name, date_of_birth, gender, marital_status}",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "complete_address",
            "Category": "Completed Information",
            "Checklist Item": "Complete Address Information",
            "Current Logic": "Check required fields: street, city, province, postal_code",
            "Application Data Used": "applicant_info.address.{street, city, province, postal_code}",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "complete_vehicle_info",
            "Category": "Completed Information",
            "Checklist Item": "Complete Vehicle Information",
            "Current Logic": "Check required fields: year, make, model, vin",
            "Application Data Used": "vehicles[].{year, make, model, vin}",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "purchase_price_provided",
            "Category": "Completed Information",
            "Checklist Item": "Purchase Price/Value provided for financed/leased vehicles",
            "Current Logic": "Check if purchase price exists for financed/leased vehicles",
            "Application Data Used": "vehicles[].list_price (if financed)",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "lienholder_info",
            "Category": "Completed Information",
            "Checklist Item": "Lienholder information complete for financed vehicles",
            "Current Logic": "Currently placeholder - needs implementation",
            "Application Data Used": "Currently placeholder",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        
        # Driver/MVR
        {
            "ID": "mvr_matches_application",
            "Category": "Driver/MVR",
            "Checklist Item": "MVR information matches application",
            "Current Logic": "Compare driver details: license_number, date_of_birth, name",
            "Application Data Used": "drivers[].{license_number, date_of_birth, name}",
            "Quote Data Used": "drivers[].{licence_number, birth_date, full_name}",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "license_class_valid",
            "Category": "Driver/MVR",
            "Checklist Item": "License class appropriate for vehicle type",
            "Current Logic": "Check if license class is G, G1, or G2",
            "Application Data Used": "drivers[].license_class",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "conviction_disclosure",
            "Category": "Driver/MVR",
            "Checklist Item": "All convictions properly disclosed",
            "Current Logic": "Compare conviction count between application and quote",
            "Application Data Used": "convictions[]",
            "Quote Data Used": "convictions[]",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "driver_training_valid",
            "Category": "Driver/MVR",
            "Checklist Item": "Driver training certificates valid if claimed",
            "Current Logic": "If training=Yes, check if training_date exists",
            "Application Data Used": "drivers[].{driver_training, driver_training_date}",
            "Quote Data Used": "Not used",
            "Current Status": "Warning (Required=False)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        
        # Coverage Requirements
        {
            "ID": "coverage_limits_appropriate",
            "Category": "Coverage Requirements",
            "Checklist Item": "Coverage limits appropriate for risk",
            "Current Logic": "Check for minimum $1M liability coverage",
            "Application Data Used": "Not used",
            "Quote Data Used": "coverages[].{type, limit}",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "opcf_43_applicable",
            "Category": "Coverage Requirements",
            "Checklist Item": "OPCF 43 applied where applicable",
            "Current Logic": "Currently placeholder - needs business rules",
            "Application Data Used": "Placeholder",
            "Quote Data Used": "Placeholder",
            "Current Status": "Warning (Required=False)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "opcf_28a_applicable",
            "Category": "Coverage Requirements",
            "Checklist Item": "OPCF 28a applied where applicable",
            "Current Logic": "Currently placeholder - needs business rules",
            "Application Data Used": "Placeholder",
            "Quote Data Used": "Placeholder",
            "Current Status": "Warning (Required=False)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "pleasure_use_remarks",
            "Category": "Coverage Requirements",
            "Checklist Item": "Pleasure Use Remarks",
            "Current Logic": "Check if remarks exist for pleasure use vehicles",
            "Application Data Used": "Not used",
            "Quote Data Used": "vehicles[].{primary_use, remarks}",
            "Current Status": "Warning (Required=False)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        
        # Forms
        {
            "ID": "ribo_disclosure",
            "Category": "Forms",
            "Checklist Item": "RIBO Disclosure Form completed",
            "Current Logic": "Currently placeholder - needs implementation",
            "Application Data Used": "Placeholder",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "privacy_consent",
            "Category": "Forms",
            "Checklist Item": "Privacy Consent Form signed",
            "Current Logic": "Currently placeholder - needs implementation",
            "Application Data Used": "Placeholder",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "accident_benefit_selection",
            "Category": "Forms",
            "Checklist Item": "Accident Benefit Selection Form completed",
            "Current Logic": "Check if accident_benefits field exists",
            "Application Data Used": "coverage_info.accident_benefits",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        
        # Other Requirements
        {
            "ID": "payment_method_valid",
            "Category": "Other Requirements",
            "Checklist Item": "Valid payment method provided",
            "Current Logic": "Check if payment_frequency field exists",
            "Application Data Used": "policy_info.payment_frequency",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "broker_signature",
            "Category": "Other Requirements",
            "Checklist Item": "Broker signature and license number",
            "Current Logic": "Check if broker_name exists",
            "Application Data Used": "application_info.broker_name",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        },
        {
            "ID": "application_complete",
            "Category": "Other Requirements",
            "Checklist Item": "Application form completely filled out",
            "Current Logic": "Check if key sections exist: applicant_info, vehicles, drivers",
            "Application Data Used": "{applicant_info, vehicles, drivers} exist",
            "Quote Data Used": "Not used",
            "Current Status": "Critical (Required=True)",
            "Keep/Remove/Modify": "REVIEW",
            "Your Comments": "",
            "New Logic (if different)": ""
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(checklist_data)
    
    # Create Excel workbook with formatting
    wb = Workbook()
    ws = wb.active
    ws.title = "QC Checklist Review"
    
    # Add headers
    headers = list(df.columns)
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(
            left=Side(border_style="thin"),
            right=Side(border_style="thin"),
            top=Side(border_style="thin"),
            bottom=Side(border_style="thin")
        )
    
    # Add data
    for row_num, row_data in enumerate(df.values, 2):
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            cell.border = Border(
                left=Side(border_style="thin"),
                right=Side(border_style="thin"),
                top=Side(border_style="thin"),
                bottom=Side(border_style="thin")
            )
            
            # Color code based on category
            if col_num == 2:  # Category column
                if value == "Signatures":
                    cell.fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
                elif value == "Completed Information":
                    cell.fill = PatternFill(start_color="F3E5F5", end_color="F3E5F5", fill_type="solid")
                elif value == "Driver/MVR":
                    cell.fill = PatternFill(start_color="E8F5E8", end_color="E8F5E8", fill_type="solid")
                elif value == "Coverage Requirements":
                    cell.fill = PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid")
                elif value == "Forms":
                    cell.fill = PatternFill(start_color="FFEBEE", end_color="FFEBEE", fill_type="solid")
                elif value == "Other Requirements":
                    cell.fill = PatternFill(start_color="F1F8E9", end_color="F1F8E9", fill_type="solid")
            
            # Highlight Keep/Remove/Modify column
            if col_num == 8:  # Keep/Remove/Modify column
                cell.fill = PatternFill(start_color="FFFDE7", end_color="FFFDE7", fill_type="solid")
                cell.font = Font(bold=True, color="FF6600")
            
            # Highlight Your Comments column
            if col_num == 9:  # Your Comments column
                cell.fill = PatternFill(start_color="E8F5E8", end_color="E8F5E8", fill_type="solid")
                cell.font = Font(color="0066CC")
    
    # Auto-adjust column widths
    column_widths = {
        'A': 20,  # ID
        'B': 18,  # Category
        'C': 35,  # Checklist Item
        'D': 40,  # Current Logic
        'E': 30,  # Application Data Used
        'F': 25,  # Quote Data Used
        'G': 20,  # Current Status
        'H': 15,  # Keep/Remove/Modify
        'I': 40,  # Your Comments
        'J': 40   # New Logic
    }
    
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width
    
    # Set row heights
    for row in range(2, len(checklist_data) + 2):
        ws.row_dimensions[row].height = 60
    
    # Add instructions sheet
    ws2 = wb.create_sheet("Instructions")
    instructions = [
        ["INSTRUCTIONS FOR REVIEWING QC CHECKLIST", ""],
        ["", ""],
        ["1. Review Each Item:", "Look at each QC checklist item and its current logic"],
        ["", ""],
        ["2. In 'Keep/Remove/Modify' column, specify:", ""],
        ["   - KEEP", "Keep the item as-is"],
        ["   - REMOVE", "Remove this item from checklist"],
        ["   - MODIFY", "Keep item but change the logic"],
        ["", ""],
        ["3. In 'Your Comments' column:", "Add your feedback, business rules, or concerns"],
        ["", ""],
        ["4. In 'New Logic' column:", "If MODIFY, describe the new logic you want"],
        ["", ""],
        ["Examples:", ""],
        ["", ""],
        ["Keep/Remove/Modify: MODIFY", ""],
        ["Your Comments: Date should allow 30-day variance, not exact match", ""],
        ["New Logic: Allow application date within 30 days of effective date", ""],
        ["", ""],
        ["Keep/Remove/Modify: REMOVE", ""],
        ["Your Comments: We don't use OPCF 43 in our business", ""],
        ["", ""],
        ["Keep/Remove/Modify: KEEP", ""],
        ["Your Comments: This is correct as-is", ""],
        ["", ""],
        ["CATEGORIES EXPLAINED:", ""],
        ["", ""],
        ["Signatures:", "Checking for proper signatures and date matching"],
        ["Completed Information:", "Ensuring all required fields are filled"],
        ["Driver/MVR:", "Validating driver information and MVR consistency"],
        ["Coverage Requirements:", "Checking coverage limits and endorsements"],
        ["Forms:", "Validating required forms are complete"],
        ["Other Requirements:", "Payment methods, broker info, etc."]
    ]
    
    for row_num, (col1, col2) in enumerate(instructions, 1):
        ws2.cell(row=row_num, column=1, value=col1).font = Font(bold=True if col1 and not col1.startswith(" ") else False)
        ws2.cell(row=row_num, column=2, value=col2)
    
    ws2.column_dimensions['A'].width = 40
    ws2.column_dimensions['B'].width = 50
    
    # Save the file
    filename = "QC_Checklist_Review.xlsx"
    wb.save(filename)
    
    print(f"✅ Excel file created: {filename}")
    print(f"📊 Contains {len(checklist_data)} QC checklist items")
    print(f"📝 Please review and update the 'Keep/Remove/Modify' and 'Your Comments' columns")
    
    # Also create a CSV version
    csv_filename = "QC_Checklist_Review.csv"
    df.to_csv(csv_filename, index=False)
    print(f"📋 CSV file also created: {csv_filename}")
    
    return filename, csv_filename

if __name__ == "__main__":
    create_qc_checklist_excel()

