from flask import Flask, request, jsonify, send_file, render_template
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

VIDEO_PATH = os.path.join(UPLOAD_FOLDER, 'input.mp4')

@app.route('/')
def index():
    return render_template('project_template.html')

@app.route('/upload', methods=['POST'])
def upload():
    print("Upload request received")
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Delete existing video first (only one video at a time)
    if os.path.exists(VIDEO_PATH):
        os.remove(VIDEO_PATH)
    
    try:
        file.save(VIDEO_PATH)
        print(f"File saved to {VIDEO_PATH}")
        return jsonify({'message': 'Video uploaded successfully'}), 200
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/delete', methods=['DELETE'])
def delete():
    try:
        if os.path.exists(VIDEO_PATH):
            os.remove(VIDEO_PATH)
            print(f"Deleted: {VIDEO_PATH}")
        return jsonify({'message': 'Video deleted successfully'}), 200
    except Exception as e:
        print(f"Delete error: {e}")
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

@app.route('/stream', methods=['GET'])
def stream():
    print("Stream request received")
    print(f"VIDEO_PATH exists: {os.path.exists(VIDEO_PATH)}")
    
    try:
        if os.path.exists(VIDEO_PATH):
            print(f"Serving video: {VIDEO_PATH}")
            return send_file(VIDEO_PATH, mimetype='video/mp4', conditional=True)
        else:
            print("No video file found")
            return jsonify({'error': 'No video available'}), 404
    except Exception as e:
        print(f"Stream error: {e}")
        return jsonify({'error': f'Streaming failed: {str(e)}'}), 500

# Debug endpoint
@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'video_uploaded': os.path.exists(VIDEO_PATH),
        'video_path': VIDEO_PATH
    })

# Set max file size to 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

if __name__ == '__main__':
    app.run(debug=True, port=5000)
