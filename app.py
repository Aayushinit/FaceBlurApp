from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def blur_faces(image_path):
    """Detect and blur faces in the image."""
    # Load the Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Read the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    # Blur each detected face
    for (x, y, w, h) in faces:
        face_region = image[y:y+h, x:x+w]
        blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
        image[y:y+h, x:x+w] = blurred_face
    
    # Save the modified image
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'blurred_' + os.path.basename(image_path))
    cv2.imwrite(output_path, image)
    
    return output_path

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check for file in request
    if 'file' not in request.files:
        return jsonify({"error": "No file part", "success": False}), 400
    
    file = request.files['file']
    
    # Validate file selection
    if file.filename == '':
        return jsonify({"error": "No selected file", "success": False}), 400
    
    # Validate file type and size
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type", "success": False}), 400
    
    if file.content_length > MAX_FILE_SIZE:
        return jsonify({"error": "File exceeds 10MB limit", "success": False}), 400
    
    try:
        # Secure filename and create timestamp
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(upload_path)
        
        # Process image to blur faces
        output_path = blur_faces(upload_path)
        
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error processing image"
        }), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
