from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

from extractors.mvr_extractor import extract_mvr_data
from extractors.dash_extractor import extract_dash_data
from extractors.quote_extractor import extract_quote_data
from validator.compare_engine import validate_quote
from quote_comparison_service import compare_quote_with_pdf

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    results = {
        "mvrs": [],
        "dashes": [],
        "quotes": []
    }

    print(f"Processing {len(files)} files...")

    # First pass: extract MVR and Dash data
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            
            print(f"Processing file: {filename}")

            try:
                if "MVR" in filename.upper():
                    mvr_data = extract_mvr_data(path)
                    print(f"MVR extracted: {mvr_data.get('licence_number', 'No license')} - {mvr_data.get('name', 'No name')}")
                    results["mvrs"].append(mvr_data)
                elif "DASH" in filename.upper():
                    dash_data = extract_dash_data(path)
                    print(f"DASH extracted: {len(dash_data.get('claims', []))} claims")
                    results["dashes"].append(dash_data)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                # Continue processing other files

    # Second pass: extract quote data with MVR integration
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                if "QUOTE" in filename.upper():
                    # Pass MVR data to quote extractor for conviction integration
                    quote_data = extract_quote_data(path, results["mvrs"])
                    print(f"Quote extracted: {len(quote_data.get('drivers', []))} drivers, {len(quote_data.get('vehicles', []))} vehicles, {len(quote_data.get('convictions', []))} convictions")
                    results["quotes"].append(quote_data)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                # Continue processing other files

    print(f"Extraction complete. MVRs: {len(results['mvrs'])}, DASHes: {len(results['dashes'])}, Quotes: {len(results['quotes'])}")

    try:
        validation_report = validate_quote(results)
        print("Validation completed successfully")
    except Exception as e:
        print(f"Validation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "extracted": results,
        "validation_report": validation_report
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
    
    return jsonify(debug_results)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
