from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

from extractors.mvr_extractor import extract_mvr_data
from extractors.dash_extractor import extract_dash_data
from extractors.quote_extractor import extract_quote_data
from validator.compare_engine import validate_quote

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

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            if "MVR" in filename.upper():
                results["mvrs"].append(extract_mvr_data(path))
            elif "DASH" in filename.upper():
                results["dashes"].append(extract_dash_data(path))
            elif "QUOTE" in filename.upper():
                results["quotes"].append(extract_quote_data(path))

    validation_report = validate_quote(results)

    return jsonify({
        "extracted": results,
        "validation_report": validation_report
    })

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
