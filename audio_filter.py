import numpy as np
import soundfile as sf
import subprocess
import os

def apply_preemphasis(input_path, output_path, alpha=0.97):
    """
    Apply pre-emphasis filter: y[n] = x[n] - α * x[n-1]
    """
    try:
        # Convert to absolute paths
        input_path = os.path.abspath(input_path)
        output_path = os.path.abspath(output_path)
        
        print(f"Audio filter input: {input_path}")
        print(f"Audio filter output: {output_path}")
        
        # Check if input file exists
        if not os.path.exists(input_path):
            return False, f"Input file not found: {input_path}"
        
        # STEP 1: Extract audio from MP4 using FFmpeg
        output_dir = os.path.dirname(output_path)
        extracted_audio_path = os.path.join(output_dir, 'extracted_audio.wav')
        
        print("Extracting audio from MP4...")
        extract_cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM format for soundfile
            '-ar', '44100',  # Sample rate
            '-ac', '2',      # Stereo
            extracted_audio_path
        ]
        
        subprocess.run(extract_cmd, check=True, capture_output=True, text=True)
        print(f"Audio extracted to: {extracted_audio_path}")
        
        # STEP 2: Read the extracted audio with soundfile
        audio_data, sample_rate = sf.read(extracted_audio_path)
        print(f"Audio loaded: shape={audio_data.shape}, sample_rate={sample_rate}")
        
        # STEP 3: Apply pre-emphasis filter
        if len(audio_data.shape) > 1:
            processed_audio = np.zeros_like(audio_data)
            for channel in range(audio_data.shape[1]):
                processed_audio[:, channel] = preemphasis_filter(audio_data[:, channel], alpha)
        else:
            processed_audio = preemphasis_filter(audio_data, alpha)
        
        # STEP 4: Save processed audio
        processed_audio_path = os.path.join(output_dir, 'processed_audio.wav')
        sf.write(processed_audio_path, processed_audio, sample_rate)
        print(f"Processed audio saved: {processed_audio_path}")
        
        # STEP 5: Combine processed audio with original video
        cmd = [
            'ffmpeg', '-y', 
            '-i', input_path,           # Original video
            '-i', processed_audio_path, # Processed audio
            '-c:v', 'copy',             # Copy video without re-encoding
            '-c:a', 'aac',              # Encode audio as AAC
            '-map', '0:v:0',            # Use video from first input
            '-map', '1:a:0',            # Use audio from second input
            output_path
        ]
        
        print(f"Combining video and processed audio...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("FFmpeg completed successfully")
        
        # STEP 6: Clean up temporary files
        for temp_file in [extracted_audio_path, processed_audio_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Cleaned up: {temp_file}")
        
        # Check if output file was created
        if os.path.exists(output_path):
            print(f"Output file created successfully: {output_path}")
            return True, "Pre-emphasis filter applied successfully"
        else:
            return False, "Output file was not created"
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        # Clean up temporary files
        cleanup_temp_files(output_dir)
        return False, f"FFmpeg failed: {e.stderr}"
        
    except Exception as e:
        print(f"Pre-emphasis filter error: {str(e)}")
        # Clean up temporary files
        cleanup_temp_files(output_dir)
        return False, f"Pre-emphasis filter failed: {str(e)}"

def cleanup_temp_files(output_dir):
    """Clean up temporary audio files"""
    temp_files = ['extracted_audio.wav', 'processed_audio.wav']
    for temp_file in temp_files:
        temp_path = os.path.join(output_dir, temp_file)
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Cleaned up: {temp_path}")

def preemphasis_filter(signal, alpha=0.97):
    """
    Implement the pre-emphasis formula: y[n] = x[n] - α * x[n-1]
    """
    # Create output array
    emphasized = np.zeros_like(signal)
    
    # First sample remains unchanged
    emphasized[0] = signal[0]
    
    # Apply pre-emphasis formula for remaining samples
    for n in range(1, len(signal)):
        emphasized[n] = signal[n] - alpha * signal[n-1]
    
    return emphasized

def apply_audio_filter(filter_name, input_path, output_path, **kwargs):
    """Main function to apply audio filters"""
    if filter_name == "preemphasis":
        alpha = kwargs.get('alpha', 0.97)
        return apply_preemphasis(input_path, output_path, alpha)
    else:
        return False, f"Unknown audio filter: {filter_name}"
