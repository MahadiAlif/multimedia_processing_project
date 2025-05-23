from flask import Flask, request, jsonify, send_file, render_template
import os

from audio_filter import apply_audio_filter
from video_filter import apply_video_filter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

VIDEO_PATH = os.path.join(UPLOAD_FOLDER, 'input.mp4')
OUTPUT_PATH = os.path.join(PROCESSED_FOLDER, 'output.mp4')

CURRENT_FILTER = None

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

@app.route('/configure', methods=['POST'])
def configure():
    global CURRENT_FILTER
    try:
        data = request.get_json()
        filter_name = data.get('filter', None)
        
        # Validate filter
        available_filters = ['preemphasis', 'grayscale']
        if filter_name not in available_filters:
            return jsonify({'error': f'Invalid filter. Available: {available_filters}'}), 400
        
        CURRENT_FILTER = filter_name
        print(f"Filter configured: {CURRENT_FILTER}")
        return jsonify({'message': f'Filter set to: {CURRENT_FILTER}'}), 200
    except Exception as e:
        print(f"Configure error: {e}")
        return jsonify({'error': f'Configuration failed: {str(e)}'}), 500

@app.route('/apply', methods=['POST'])
def apply():
    if not os.path.exists(VIDEO_PATH):
        return jsonify({'error': 'No video uploaded'}), 400
    
    if not CURRENT_FILTER:
        return jsonify({'error': 'No filter configured'}), 400

    try:
        # Remove existing processed video
        if os.path.exists(OUTPUT_PATH):
            os.remove(OUTPUT_PATH)
        
        # Ensure paths are absolute
        input_path = os.path.abspath(VIDEO_PATH)
        output_path = os.path.abspath(OUTPUT_PATH)
        
        print(f"Applying filter: {CURRENT_FILTER}")
        print(f"Input path: {input_path}")
        print(f"Output path: {output_path}")
        
        # Check if input file actually exists
        if not os.path.exists(input_path):
            return jsonify({'error': f'Input video file not found: {input_path}'}), 400
        
        # Apply single filter
        success = False
        message = ""
        
        if CURRENT_FILTER == 'preemphasis':
            print("Applying pre-emphasis audio filter")
            success, message = apply_audio_filter('preemphasis', input_path, output_path, alpha=0.97)
            
        elif CURRENT_FILTER == 'grayscale':
            print("Applying grayscale video filter")
            success, message = apply_video_filter('grayscale', input_path, output_path)
        
        if not success:
            print(f"Filter application failed: {message}")
            return jsonify({'error': message}), 500
        
        # Verify output file was created
        if not os.path.exists(output_path):
            return jsonify({'error': 'Output file was not created successfully'}), 500
        
        print(f"Filter {CURRENT_FILTER} applied successfully")
        print(f"Output file size: {os.path.getsize(output_path)} bytes")
        
        return jsonify({'message': f'{CURRENT_FILTER.title()} filter applied successfully'}), 200
        
    except Exception as e:
        print(f"Apply error: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    
@app.route('/stream', methods=['GET'])
def stream():
    print("Stream request received")
    print(f"OUTPUT_PATH exists: {os.path.exists(OUTPUT_PATH)}")
    print(f"VIDEO_PATH exists: {os.path.exists(VIDEO_PATH)}")
    
    try:
        # Serve processed video if available, otherwise serve original
        if os.path.exists(OUTPUT_PATH):
            print(f"Serving processed video: {OUTPUT_PATH}")
            return send_file(OUTPUT_PATH, mimetype='video/mp4', conditional=True)
        elif os.path.exists(VIDEO_PATH):
            print(f"Serving original video: {VIDEO_PATH}")
            return send_file(VIDEO_PATH, mimetype='video/mp4', conditional=True)
        else:
            print("No video files found")
            return jsonify({'error': 'No video available'}), 404
    except Exception as e:
        print(f"Stream error: {e}")
        return jsonify({'error': f'Streaming failed: {str(e)}'}), 500
# Debug endpoint
@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'video_uploaded': os.path.exists(VIDEO_PATH),
        'video_processed': os.path.exists(OUTPUT_PATH),
        'current_filter': CURRENT_FILTER,
        'available_filters': ['preemphasis', 'grayscale']
    })

# Set max file size to 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

if __name__ == '__main__':
    app.run(debug=True, port=5000)

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
