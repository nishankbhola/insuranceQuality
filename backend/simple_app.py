from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import json

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Quality Control API is running",
        "version": "1.0.0"
    })

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        "message": "Quality Control API is working!",
        "endpoint": "/quality/api/test"
    })

@app.route('/api/validate', methods=['POST'])
def validate_documents():
    """Test endpoint for document validation"""
    # Check for different possible field names
    quote_files = request.files.getlist('quote')
    mvr_files = request.files.getlist('mvr')
    dash_files = request.files.getlist('dash')
    
    all_files = quote_files + mvr_files + dash_files
    
    if not all_files:
        return jsonify({"error": "No files provided"}), 400

    results = {
        "status": "success",
        "message": "Files received successfully",
        "file_count": len(all_files),
        "files": [],
        "validation_report": {
            "drivers": [
                {
                    "driver_name": "Test Driver",
                    "driver_license": "A1234-56789012-345678",
                    "mvr_score": 85,
                    "license_progression_score": 90,
                    "convictions_score": 95,
                    "dash_score": 88,
                    "driver_training_score": 92,
                    "overall_score": 90,
                    "issues": [
                        {
                            "type": "warning",
                            "message": "Sample validation completed successfully",
                            "severity": "low"
                        }
                    ]
                }
            ]
        }
    }

    for file in all_files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            results["files"].append({
                "name": filename,
                "size": len(file.read()),
                "type": "PDF"
            })
            file.seek(0)  # Reset file pointer

    return jsonify(results)

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
        
        # Return sample data for now
        application_data = {
            "applicant_info": {
                "full_name": "Sample Applicant",
                "email": "sample@example.com",
                "phone": "555-123-4567"
            },
            "vehicles": [
                {
                    "year": "2020",
                    "make": "Toyota",
                    "model": "Camry",
                    "vin": "1HGBH41JXMN109186"
                }
            ],
            "drivers": [
                {
                    "name": "Sample Driver",
                    "license_number": "A1234-56789012-345678",
                    "license_class": "G"
                }
            ]
        }
        
        return jsonify({
            "message": "Application data extracted successfully",
            "filename": "application_data.json",
            "data": application_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Application processing failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 