import subprocess
import os

def apply_grayscale(input_path, output_path):
    """
    Convert video to grayscale using FFmpeg.
    """
    try:
        # Convert to absolute paths
        input_path = os.path.abspath(input_path)
        output_path = os.path.abspath(output_path)
        
        print(f"Video filter input: {input_path}")
        print(f"Video filter output: {output_path}")
        
        # Check if input file exists
        if not os.path.exists(input_path):
            return False, f"Input file not found: {input_path}"
        
        # FFmpeg command to convert to grayscale
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', 'hue=s=0',      # Remove saturation to make grayscale
            '-c:a', 'copy',        # Copy audio without re-encoding
            '-c:v', 'libx264',     # Use H.264 for video encoding
            '-preset', 'fast',     # Fast encoding preset
            output_path
        ]
        
        print(f"Running FFmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("FFmpeg completed successfully")
        
        # Check if output file was created
        if os.path.exists(output_path):
            print(f"Output file created successfully: {output_path}")
            return True, "Grayscale filter applied successfully"
        else:
            return False, "Output file was not created"
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return False, f"Grayscale filter failed: {e.stderr}"
    except Exception as e:
        print(f"Video filter error: {str(e)}")
        return False, f"Grayscale filter failed: {str(e)}"

def apply_video_filter(filter_name, input_path, output_path, **kwargs):
    """Main function to apply video filters"""
    if filter_name == "grayscale":
        return apply_grayscale(input_path, output_path)
    else:
        return False, f"Unknown video filter: {filter_name}"
