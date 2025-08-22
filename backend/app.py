from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import glob
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from extractors.mvr_extractor import extract_mvr_data
from extractors.dash_extractor import extract_dash_data
from extractors.quote_extractor import extract_quote_data
from validator.compare_engine import validate_quote, ValidationEngine
from quote_comparison_service import compare_quote_with_pdf
from extractors.gemini_application_extractor import extract_and_validate_application_qc

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cleanup_upload_folder():
    """Clean up all PDF files and debug files in the uploads folder and backend directory after processing"""
    try:
        # Clean up PDF files in uploads folder (but preserve cleaned PDFs)
        pdf_files = glob.glob(os.path.join(UPLOAD_FOLDER, "*.pdf"))
        for pdf_file in pdf_files:
            try:
                # Don't delete cleaned PDFs - they might be needed for debugging
                if "_cleaned.pdf" not in os.path.basename(pdf_file):
                    os.remove(pdf_file)
                    print(f"Cleaned up PDF: {os.path.basename(pdf_file)}")
                else:
                    print(f"Preserving cleaned PDF: {os.path.basename(pdf_file)}")
            except Exception as e:
                print(f"Error deleting {pdf_file}: {e}")
        
        # Clean up debug text files in uploads folder (MVR_debug_*.txt, etc.)
        debug_files = glob.glob(os.path.join(UPLOAD_FOLDER, "*_debug_*.txt"))
        for debug_file in debug_files:
            try:
                os.remove(debug_file)
                print(f"Cleaned up debug file: {os.path.basename(debug_file)}")
            except Exception as e:
                print(f"Error deleting {debug_file}: {e}")
        
        # Clean up temporary files in uploads folder
        temp_files = glob.glob(os.path.join(UPLOAD_FOLDER, "temp_*.pdf"))
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                print(f"Cleaned up temp file: {os.path.basename(temp_file)}")
            except Exception as e:
                print(f"Error deleting {temp_file}: {e}")
        
        # Clean up debug files in backend directory
        backend_debug_files = glob.glob("MVR_debug_*.txt")
        for debug_file in backend_debug_files:
            try:
                os.remove(debug_file)
                print(f"Cleaned up backend debug file: {debug_file}")
            except Exception as e:
                print(f"Error deleting {debug_file}: {e}")
                
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Clean up any leftover files from previous runs on startup
print("Cleaning up leftover files from previous runs...")
cleanup_upload_folder()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_file_type(file):
    """Automatically detect file type based on filename and content analysis"""
    filename = file.filename.lower()
    
    # First, try to detect based on filename patterns
    if any(keyword in filename for keyword in ['quote', 'insurance', 'policy']):
        return 'quote'
    elif any(keyword in filename for keyword in ['mvr', 'motor', 'vehicle', 'record']):
        return 'mvr'
    elif any(keyword in filename for keyword in ['dash', 'abstract', 'history', 'claims']):
        return 'dash'
    
    # If filename doesn't give clear indication, we'll need to analyze content
    # For now, we'll return 'auto' and let the backend handle it
    return 'auto'

def analyze_file_content(file_path):
    """Analyze file content to determine its type"""
    try:
        # Try to extract data from each extractor and see which one works
        # This is a simple heuristic approach
        
        # Try MVR extraction
        try:
            mvr_data = extract_mvr_data(file_path)
            if mvr_data and mvr_data.get('licence_number'):
                return 'mvr'
        except:
            pass
        
        # Try DASH extraction
        try:
            dash_data = extract_dash_data(file_path)
            if dash_data and (dash_data.get('claims') or dash_data.get('policies')):
                return 'dash'
        except:
            pass
        
        # Try Quote extraction
        try:
            quote_data = extract_quote_data(file_path)
            if quote_data and (quote_data.get('drivers') or quote_data.get('vehicles')):
                return 'quote'
        except:
            pass
        
        # If none work, return None
        return None
    except Exception as e:
        print(f"Error analyzing file content: {e}")
        return None

@app.route('/api/validate', methods=['POST'])
def validate_documents():
    """New unified endpoint for document validation with automatic file type detection"""
    if 'quote' not in request.files and 'mvr' not in request.files and 'dash' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    # Check if noDashReport flag is set
    no_dash_report = request.form.get('noDashReport', 'false').lower() == 'true'
    
    files = request.files
    results = {
        "mvrs": [],
        "dashes": [],
        "quotes": []
    }
    
    print(f"Processing files for validation... (noDashReport: {no_dash_report})")
    
    # First pass: Extract MVR and DASH data (these don't depend on other data)
    print("=== FIRST PASS: Processing MVR and DASH files ===")
    for field_name in request.files.keys():
        if field_name in ['mvr', 'dash']:
            files_for_field = request.files.getlist(field_name)
            
            for file in files_for_field:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                    
                    print(f"Processing {field_name} file: {filename}")
                    
                    try:
                        if field_name == 'mvr':
                            mvr_data = extract_mvr_data(path)
                            print(f"MVR extracted: {mvr_data.get('licence_number', 'No license')} - {mvr_data.get('name', 'No name')}")
                            results["mvrs"].append(mvr_data)
                        elif field_name == 'dash':
                            dash_data = extract_dash_data(path)
                            print(f"DASH extracted: {len(dash_data.get('claims', []))} claims")
                            results["dashes"].append(dash_data)
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        import traceback
                        traceback.print_exc()
    
    print(f"=== FIRST PASS COMPLETE: {len(results['mvrs'])} MVRs and {len(results['dashes'])} DASH reports extracted ===")
    
    # Second pass: Extract quote data with complete MVR data available
    print("=== SECOND PASS: Processing Quote files with MVR data available ===")
    for field_name in request.files.keys():
        if field_name == 'quote':
            files_for_field = request.files.getlist(field_name)
            
            for file in files_for_field:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                    
                    print(f"Processing quote file: {filename} with {len(results['mvrs'])} MVRs available")
                    
                    try:
                        quote_data = extract_quote_data(path, results["mvrs"])
                        print(f"Quote extracted: {len(quote_data.get('drivers', []))} drivers")
                        results["quotes"].append(quote_data)
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        import traceback
                        traceback.print_exc()
    
    # Handle auto-detection for any remaining files
    for field_name in request.files.keys():
        if field_name not in ['quote', 'mvr', 'dash']:
            files_for_field = request.files.getlist(field_name)
            
            for file in files_for_field:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                    
                    print(f"Auto-detecting file type for: {filename}")
                    
                    try:
                        detected_type = analyze_file_content(path)
                        if detected_type == 'quote':
                            quote_data = extract_quote_data(path, results["mvrs"])
                            results["quotes"].append(quote_data)
                        elif detected_type == 'mvr':
                            mvr_data = extract_mvr_data(path)
                            print(f"MVR extracted (auto-detected): {mvr_data.get('licence_number', 'No license')} - {mvr_data.get('name', 'No name')}")
                            results["mvrs"].append(mvr_data)
                        elif detected_type == 'dash':
                            dash_data = extract_dash_data(path)
                            results["dashes"].append(dash_data)
                        else:
                            print(f"Could not determine type for {filename}")
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        import traceback
                        traceback.print_exc()
    
    print(f"Extraction complete. MVRs: {len(results['mvrs'])}, DASHes: {len(results['dashes'])}, Quotes: {len(results['quotes'])}")
    
    # Validate that we have all required documents
    if not results["quotes"]:
        return jsonify({"error": "No valid quote document found"}), 400
    if not results["mvrs"]:
        return jsonify({"error": "No valid MVR document found"}), 400
    
    # Only require DASH if noDashReport is not set
    if not no_dash_report and not results["dashes"]:
        return jsonify({"error": "No valid DASH document found"}), 400
    
    try:
        # Pass the noDashReport flag to the validation engine
        validation_report = validate_quote(results, no_dash_report=no_dash_report)
        print("Validation completed successfully")
        
    except Exception as e:
        print(f"Validation error: {e}")
        import traceback
        traceback.print_exc()
        # Clean up files even if validation fails
        cleanup_upload_folder()
        return jsonify({"error": str(e)}), 500
    
    # Clean up uploaded PDF files after successful processing
    cleanup_upload_folder()
    
    return jsonify({
        "extracted": results,
        "validation_report": validation_report,
        "no_dash_report": no_dash_report
    })

@app.route('/api/validate-compact', methods=['POST'])
def validate_documents_compact():
    """Compact validation endpoint that returns a one-page professional report with charts"""
    if 'quote' not in request.files and 'mvr' not in request.files and 'dash' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    # Check if noDashReport flag is set
    no_dash_report = request.form.get('noDashReport', 'false').lower() == 'true'
    
    files = request.files
    results = {
        "mvrs": [],
        "dashes": [],
        "quotes": []
    }
    
    print(f"Processing files for compact validation... (noDashReport: {no_dash_report})")
    
    # First pass: Extract MVR and DASH data (these don't depend on other data)
    print("=== FIRST PASS: Processing MVR and DASH files ===")
    for field_name in request.files.keys():
        if field_name in ['mvr', 'dash']:
            files_for_field = request.files.getlist(field_name)
            
            for file in files_for_field:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                    
                    print(f"Processing {field_name} file: {filename}")
                    
                    try:
                        if field_name == 'mvr':
                            mvr_data = extract_mvr_data(path)
                            print(f"MVR extracted: {mvr_data.get('licence_number', 'No license')} - {mvr_data.get('name', 'No name')}")
                            results["mvrs"].append(mvr_data)
                        elif field_name == 'dash':
                            dash_data = extract_dash_data(path)
                            print(f"DASH extracted: {len(dash_data.get('claims', []))} claims")
                            results["dashes"].append(dash_data)
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        import traceback
                        traceback.print_exc()
    
    print(f"=== FIRST PASS COMPLETE: {len(results['mvrs'])} MVRs and {len(results['dashes'])} DASH reports extracted ===")
    
    # Second pass: Extract quote data with complete MVR data available
    print("=== SECOND PASS: Processing Quote files with MVR data available ===")
    for field_name in request.files.keys():
        if field_name == 'quote':
            files_for_field = request.files.getlist(field_name)
            
            for file in files_for_field:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                    
                    print(f"Processing quote file: {filename} with {len(results['mvrs'])} MVRs available")
                    
                    try:
                        quote_data = extract_quote_data(path, results["mvrs"])
                        print(f"Quote extracted: {len(quote_data.get('drivers', []))} drivers")
                        results["quotes"].append(quote_data)
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        import traceback
                        traceback.print_exc()
    
    # Handle auto-detection for any remaining files
    for field_name in request.files.keys():
        if field_name not in ['quote', 'mvr', 'dash']:
            files_for_field = request.files.getlist(field_name)
            
            for file in files_for_field:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                    
                    print(f"Auto-detecting file type for: {filename}")
                    
                    try:
                        detected_type = analyze_file_content(path)
                        if detected_type == 'quote':
                            quote_data = extract_quote_data(path, results["mvrs"])
                            results["quotes"].append(quote_data)
                        elif detected_type == 'mvr':
                            mvr_data = extract_mvr_data(path)
                            print(f"MVR extracted (auto-detected): {mvr_data.get('licence_number', 'No license')} - {mvr_data.get('name', 'No name')}")
                            results["mvrs"].append(mvr_data)
                        elif detected_type == 'dash':
                            dash_data = extract_dash_data(path)
                            results["dashes"].append(dash_data)
                        else:
                            print(f"Could not determine type for {filename}")
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        import traceback
                        traceback.print_exc()
    
    print(f"Extraction complete. MVRs: {len(results['mvrs'])}, DASHes: {len(results['dashes'])}, Quotes: {len(results['quotes'])}")
    
    # Validate that we have all required documents
    if not results["quotes"]:
        return jsonify({"error": "No valid quote document found"}), 400
    if not results["mvrs"]:
        return jsonify({"error": "No valid MVR document found"}), 400
    
    # Only require DASH if noDashReport is not set
    if not no_dash_report and not results["dashes"]:
        return jsonify({"error": "No valid DASH document found"}), 400
    
    try:
        # Generate compact report with noDashReport flag
        engine = ValidationEngine()
        compact_report = engine.generate_compact_report(results, no_dash_report=no_dash_report)
        print("Compact validation report generated successfully")
        
    except Exception as e:
        print(f"Compact validation error: {e}")
        import traceback
        traceback.print_exc()
        # Clean up files even if validation fails
        cleanup_upload_folder()
        return jsonify({"error": str(e)}), 500
    
    # Clean up uploaded PDF files after successful processing
    cleanup_upload_folder()
    
    return jsonify({
        "compact_report": compact_report,
        "no_dash_report": no_dash_report
    })



@app.route('/compare-quote', methods=['POST'])
def compare_quote():
    """Compare uploaded PDF with quote_result.json data"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
    try:
        result = compare_quote_with_pdf(file)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Comparison failed: {str(e)}"}), 500

@app.route('/debug', methods=['POST'])
def debug_extraction():
    """Debug endpoint to see what's being extracted from each file"""
    files = request.files.getlist('files')
    debug_results = {}
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            
            debug_results[filename] = {
                "file_type": "Unknown",
                "extracted_data": {}
            }
            
            if "MVR" in filename.upper():
                debug_results[filename]["file_type"] = "MVR"
                debug_results[filename]["extracted_data"] = extract_mvr_data(path)
            elif "DASH" in filename.upper():
                debug_results[filename]["file_type"] = "DASH"
                debug_results[filename]["extracted_data"] = extract_dash_data(path)
            elif "QUOTE" in filename.upper():
                debug_results[filename]["file_type"] = "QUOTE"
                debug_results[filename]["extracted_data"] = extract_quote_data(path)
    
    # Clean up uploaded PDF files after processing
    cleanup_upload_folder()
    
    return jsonify(debug_results)

@app.route('/api/application-qc', methods=['POST'])
def application_qc():
    """New Application QC endpoint with Gemini AI-based extraction"""
    if 'application' not in request.files:
        return jsonify({"error": "No application file provided"}), 400
    
    # Note: We only require application file now, quote is optional for this QC approach
    application_file = request.files['application']
    
    if application_file.filename == '':
        return jsonify({"error": "No application file selected"}), 400
    
    if not allowed_file(application_file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
    try:
        # Save application file
        app_filename = secure_filename(application_file.filename)
        app_path = os.path.join(app.config['UPLOAD_FOLDER'], app_filename)
        application_file.save(app_path)
        
        print(f"Processing Application QC with Gemini AI: {app_filename}")
        
        # Run new Gemini-based Application QC
        qc_results = extract_and_validate_application_qc(app_path)
        
        # Process results for UI compatibility
        failed_checks = []
        passed_checks = []
        warnings = []
        critical_errors = []
        
        # Process simple validations
        all_validations_list = []
        for key, validation in qc_results.get("simple_validations", {}).items():
            validation_entry = {
                "type": key.replace("_", " ").title(),
                "message": validation["description"],
                "status": validation["status"].upper(),
                "vehicle": "General"
            }
            
            # Create entry for all_validations with UI-compatible status
            all_validations_entry = {
                "type": key.replace("_", " ").title(),
                "message": validation["description"],
                "status": "passed" if validation["status"] == "pass" else "failed",
                "vehicle": "General"
            }
            all_validations_list.append(all_validations_entry)
            
            if validation["status"] == "pass":
                passed_checks.append(validation_entry)
            else:
                if validation.get("error_type") == "critical":
                    critical_errors.append(validation_entry)
                else:
                    warnings.append(validation_entry)
                failed_checks.append(validation_entry)
        
        # Process Gemini validations
        gemini_validations = qc_results.get("gemini_validations", {})
        if isinstance(gemini_validations, dict) and "validation_1_pleasure_use" in gemini_validations:
            validation_mappings = {
                "validation_1_pleasure_use": "Pleasure Use Validation",
                "validation_2_business_use_remarks": "Business Use Remarks",
                "validation_3_purchase_date": "Purchase Date Check",
                "validation_4_purchase_price": "Purchase Price Check", 
                "validation_5_new_used_status": "New/Used Status",
                "validation_6_owned_leased_status": "Owned/Leased Status",
                "validation_7_lease_opcf5": "Lease OPCF5 Check",
                "validation_8_household_vehicle_count": "Household Vehicle Count",
                "validation_9_additional_drivers": "Additional Drivers Check"
            }
            
            for key, description in validation_mappings.items():
                if key in gemini_validations:
                    status = gemini_validations[key]
                    validation_entry = {
                        "type": description,
                        "message": f"{description}: {status}",
                        "status": status.upper(),
                        "vehicle": "General"
                    }
                    
                    # Create a separate entry for all_validations with lowercase status for UI compatibility
                    all_validations_entry = {
                        "type": description,
                        "message": f"{description}: {status}",
                        "status": "passed" if status == "pass" else "failed",
                        "vehicle": "General"
                    }
                    
                    if status == "pass":
                        passed_checks.append(validation_entry)
                    else:
                        warnings.append(validation_entry)
                        failed_checks.append(validation_entry)
                    
                    # Add to all_validations list
                    all_validations_list.append(all_validations_entry)
        
        # Generate summary
        total_checks = len(passed_checks) + len(failed_checks)
        summary = {
            "total_checks": total_checks,
            "failed_checks": len(failed_checks),
            "passed_checks": len(passed_checks),
            "overall_status": "PASS" if len(critical_errors) == 0 else "FAIL"
        }
        
        # Create comprehensive QC validation results structure for UI compatibility
        qc_validation_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "application_file": app_filename,
            "critical_errors": critical_errors,
            "warnings": warnings,
            "passed_validations": passed_checks,
            "all_validations": all_validations_list,
            "summary": {
                "total_vehicles": gemini_validations.get("details", {}).get("total_vehicles_on_policy", 0),
                "total_drivers": 1,  # Default assumption
                "critical_errors_count": len(critical_errors),
                "warnings_count": len(warnings),
                "passed_count": len(passed_checks),
                "total_validations": total_checks
            },
            "api_usage": qc_results.get("api_usage", {
                "gemini_analysis_enabled": True,
                "calls_made_this_session": qc_results.get("api_usage", {}).get("calls_made", 0),
                "daily_limit": 50,
                "remaining_calls": qc_results.get("api_usage", {}).get("remaining_calls", 50)
            })
        }
        
        # Save results to JSON files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        app_json_filename = f"application_qc_data_{timestamp}.json"
        qc_json_filename = f"qc_results_{timestamp}.json"
        
        app_json_path = os.path.join(app.config['UPLOAD_FOLDER'], app_json_filename)
        qc_json_path = os.path.join(app.config['UPLOAD_FOLDER'], qc_json_filename)
        
        with open(app_json_path, 'w', encoding='utf-8') as f:
            json.dump(qc_results, f, indent=2, ensure_ascii=False)
        
        with open(qc_json_path, 'w', encoding='utf-8') as f:
            json.dump(qc_validation_results, f, indent=2, ensure_ascii=False)
        
        print(f"Gemini Application QC completed: {summary}")
        
        # Clean up uploaded files
        cleanup_upload_folder()
        
        return jsonify({
            "message": "Application QC completed successfully with Gemini AI",
            "summary": summary,
            "qc_results": {
                "failed_checks": failed_checks,
                "passed_checks": passed_checks
            },
            "extracted_data": {
                "application": qc_results,
                "quote": None  # No quote processing in this approach
            },
            "files": {
                "application_data": app_json_filename,
                "qc_results": qc_json_filename
            },
            "qc_validation_results": qc_validation_results
        })
    
    except Exception as e:
        print(f"Error in Gemini Application QC: {e}")
        import traceback
        traceback.print_exc()
        cleanup_upload_folder()
        return jsonify({"error": f"Application QC failed: {str(e)}"}), 500



@app.route('/api/cleanup', methods=['POST'])
def manual_cleanup():
    """Manual cleanup endpoint to remove all files from uploads folder"""
    try:
        cleanup_upload_folder()
        return jsonify({"message": "Cleanup completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Cleanup failed: {str(e)}"}), 500

@app.route('/api/download-cleaned-pdf/<filename>', methods=['GET'])
def download_cleaned_pdf(filename):
    """Download cleaned PDF file"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path) and "_cleaned.pdf" in filename:
            from flask import send_file
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({"error": "File not found or not a cleaned PDF"}), 404
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@app.route('/api/download-qc-report/<filename>', methods=['GET'])
def download_qc_report(filename):
    """Download QC validation report file (PDF or text)"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path) and "QC_Validation_Report" in filename:
            from flask import send_file
            # Set appropriate MIME type based on file extension
            if filename.endswith('.pdf'):
                return send_file(file_path, as_attachment=True, download_name=filename, mimetype='application/pdf')
            else:
                return send_file(file_path, as_attachment=True, download_name=filename, mimetype='text/plain')
        else:
            return jsonify({"error": "File not found or not a QC report"}), 404
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
