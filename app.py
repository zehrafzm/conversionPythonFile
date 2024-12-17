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
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # Get threshold values from request query params
    lower_threshold = int(request.form.get("lower_threshold", 100))
    upper_threshold = int(request.form.get("upper_threshold", 200))

    video = request.files["file"]
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"processed_{video.filename}")

    video.save(video_path)

    # Process video with dynamic Canny thresholds
    cap = cv2.VideoCapture(video_path)
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

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
