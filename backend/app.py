from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import glob
from werkzeug.utils import secure_filename
import json

from extractors.mvr_extractor import extract_mvr_data
from extractors.dash_extractor import extract_dash_data
from extractors.quote_extractor import extract_quote_data
from extractors.application_extractor import extract_application_data
from validator.compare_engine import validate_quote, ValidationEngine
from quote_comparison_service import compare_quote_with_pdf

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cleanup_upload_folder():
    """Clean up all PDF files and debug files in the uploads folder and backend directory after processing"""
    try:
        # Clean up PDF files in uploads folder
        pdf_files = glob.glob(os.path.join(UPLOAD_FOLDER, "*.pdf"))
        for pdf_file in pdf_files:
            try:
                os.remove(pdf_file)
                print(f"Cleaned up PDF: {os.path.basename(pdf_file)}")
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
    
    files = request.files
    results = {
        "mvrs": [],
        "dashes": [],
        "quotes": []
    }
    
    print(f"Processing files for validation...")
    
    # Process each field name (quote, mvr, dash)
    for field_name in request.files.keys():
        # Get all files for this field name
        files_for_field = request.files.getlist(field_name)
        
        for file in files_for_field:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                
                print(f"Processing file: {filename} (field: {field_name})")
                
                # Determine file type
                file_type = field_name  # Use the field name as primary indicator
                
                try:
                    if file_type == 'quote' or (file_type in ['quote', 'mvr', 'dash'] and 'quote' in filename.lower()):
                        quote_data = extract_quote_data(path, results["mvrs"])
                        print(f"Quote extracted: {len(quote_data.get('drivers', []))} drivers")
                        results["quotes"].append(quote_data)
                        
                    elif file_type == 'mvr' or (file_type in ['quote', 'mvr', 'dash'] and 'mvr' in filename.lower()):
                        mvr_data = extract_mvr_data(path)
                        print(f"MVR extracted: {mvr_data.get('licence_number', 'No license')} - {mvr_data.get('name', 'No name')}")
                        results["mvrs"].append(mvr_data)
                        
                    elif file_type == 'dash' or (file_type in ['quote', 'mvr', 'dash'] and 'dash' in filename.lower()):
                        dash_data = extract_dash_data(path)
                        print(f"DASH extracted: {len(dash_data.get('claims', []))} claims")
                        results["dashes"].append(dash_data)
                        
                    else:
                        # Auto-detect based on content
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
    if not results["dashes"]:
        return jsonify({"error": "No valid DASH document found"}), 400
    
    try:
        validation_report = validate_quote(results)
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
        "validation_report": validation_report
    })

@app.route('/api/validate-compact', methods=['POST'])
def validate_documents_compact():
    """Compact validation endpoint that returns a one-page professional report with charts"""
    if 'quote' not in request.files and 'mvr' not in request.files and 'dash' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files
    results = {
        "mvrs": [],
        "dashes": [],
        "quotes": []
    }
    
    print(f"Processing files for compact validation...")
    
    # Process each field name (quote, mvr, dash)
    for field_name in request.files.keys():
        # Get all files for this field name
        files_for_field = request.files.getlist(field_name)
        
        for file in files_for_field:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                
                print(f"Processing file: {filename} (field: {field_name})")
                
                # Determine file type
                file_type = field_name  # Use the field name as primary indicator
                
                try:
                    if file_type == 'quote' or (file_type in ['quote', 'mvr', 'dash'] and 'quote' in filename.lower()):
                        quote_data = extract_quote_data(path, results["mvrs"])
                        print(f"Quote extracted: {len(quote_data.get('drivers', []))} drivers")
                        results["quotes"].append(quote_data)
                        
                    elif file_type == 'mvr' or (file_type in ['quote', 'mvr', 'dash'] and 'mvr' in filename.lower()):
                        mvr_data = extract_mvr_data(path)
                        print(f"MVR extracted: {mvr_data.get('licence_number', 'No license')} - {mvr_data.get('name', 'No name')}")
                        results["mvrs"].append(mvr_data)
                        
                    elif file_type == 'dash' or (file_type in ['quote', 'mvr', 'dash'] and 'dash' in filename.lower()):
                        dash_data = extract_dash_data(path)
                        print(f"DASH extracted: {len(dash_data.get('claims', []))} claims")
                        results["dashes"].append(dash_data)
                        
                    else:
                        # Auto-detect based on content
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
    if not results["dashes"]:
        return jsonify({"error": "No valid DASH document found"}), 400
    
    try:
        # Generate compact report
        engine = ValidationEngine()
        compact_report = engine.generate_compact_report(results)
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
        "compact_report": compact_report
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
    """Application QC endpoint to extract data from insurance application PDFs"""
    if 'application' not in request.files:
        return jsonify({"error": "No application file provided"}), 400
    
    file = request.files['application']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
    try:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        
        print(f"Processing application file: {filename}")
        
        # Extract application data
        application_data = extract_application_data(path)
        
        # Save to JSON file
        json_filename = "application_data.json"
        json_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(application_data, f, indent=2, ensure_ascii=False)
        
        print(f"Application data saved to {json_path}")
        
        # Clean up uploaded PDF file after processing
        cleanup_upload_folder()
        
        return jsonify({
            "message": "Application data extracted successfully",
            "filename": json_filename,
            "data": application_data
        })
        
    except Exception as e:
        print(f"Error processing application: {e}")
        import traceback
        traceback.print_exc()
        # Clean up files even if processing fails
        cleanup_upload_folder()
        return jsonify({"error": f"Application processing failed: {str(e)}"}), 500

@app.route('/api/cleanup', methods=['POST'])
def manual_cleanup():
    """Manual cleanup endpoint to remove all files from uploads folder"""
    try:
        cleanup_upload_folder()
        return jsonify({"message": "Cleanup completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Cleanup failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
