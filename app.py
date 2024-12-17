from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

UPLOAD_FOLDER = "/tmp/uploads"  # Use /tmp for Render deployments
OUTPUT_FOLDER = "/tmp/outputs"  # Use /tmp for Render deployments
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Flask backend is running!"

@app.route("/upload", methods=["POST"])
def upload_video():
    # Check if a file was uploaded
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # Get threshold values from request form data
    lower_threshold = int(request.form.get("lower_threshold", 100))
    upper_threshold = int(request.form.get("upper_threshold", 200))

    # Get the video file from the request
    video = request.files["file"]
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"processed_{video.filename}")

    try:
        # Save the video file to disk
        video.save(video_path)

        # Process video with dynamic Canny thresholds
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return jsonify({"error": "Failed to open video file"}), 500
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, lower_threshold, upper_threshold)
            out.write(cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))

        cap.release()
        out.release()

        # Return the processed video
        return send_file(output_path, as_attachment=True, mimetype="video/mp4")
    
    except Exception as e:
        # If there's an error during processing
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)  # Ensure you specify the port correctly
