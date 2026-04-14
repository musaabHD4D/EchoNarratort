"""
Audio Merger - Combines multiple audio files into one
Fixed and improved version
"""

import os
import wave
import struct
import array
from typing import List, Optional
from pathlib import Path

from .config import Config


class AudioMerger:
    """Merge multiple audio files into a single file"""
    
    def __init__(self):
        self.supported_formats = ['.wav', '.mp3', '.ogg']
    
    def get_audio_params(self, filepath: str) -> dict:
        """Get audio file parameters"""
        try:
            with wave.open(filepath, 'rb') as wav_file:
                params = {
                    'nchannels': wav_file.getnchannels(),
                    'sampwidth': wav_file.getsampwidth(),
                    'framerate': wav_file.getframerate(),
                    'nframes': wav_file.getnframes()
                }
                return params
        except Exception as e:
            print(f"Error reading audio file {filepath}: {e}")
            return None
    
    def read_audio_data(self, filepath: str) -> bytes:
        """Read raw audio data from file"""
        try:
            with wave.open(filepath, 'rb') as wav_file:
                return wav_file.readframes(wav_file.getnframes())
        except Exception as e:
            print(f"Error reading audio data from {filepath}: {e}")
            return None
    
    def merge_files(
        self,
        input_files: List[str],
        output_path: Optional[str] = None,
        callback: Optional[callable] = None
    ) -> Optional[str]:
        """
        Merge multiple WAV audio files into one
        
        Args:
            input_files: List of paths to audio files
            output_path: Output path for merged file
            callback: Optional progress callback
            
        Returns:
            Path to merged file or None if failed
        """
        if not input_files:
            error_msg = "No input files provided"
            print(error_msg)
            if callback:
                callback(error_msg)
            return None
        
        if len(input_files) == 1:
            # Only one file, just copy it
            if output_path is None:
                output_path = input_files[0]
            elif output_path != input_files[0]:
                try:
                    import shutil
                    shutil.copy2(input_files[0], output_path)
                except Exception as e:
                    print(f"Error copying file: {e}")
                    return None
            return output_path
        
        # Validate all input files exist
        for filepath in input_files:
            if not os.path.exists(filepath):
                error_msg = f"Input file not found: {filepath}"
                print(error_msg)
                if callback:
                    callback(error_msg)
                return None
        
        if callback:
            callback("Reading audio files...")
        
        # Get parameters from first file
        first_params = self.get_audio_params(input_files[0])
        if not first_params:
            error_msg = "Could not read first audio file"
            print(error_msg)
            if callback:
                callback(error_msg)
            return None
        
        # Read all audio data
        all_audio_data = []
        total_frames = 0
        
        for i, filepath in enumerate(input_files):
            if callback:
                callback(f"Reading file {i+1}/{len(input_files)}")
            
            params = self.get_audio_params(filepath)
            if not params:
                continue
            
            # Check compatibility (warn but continue)
            if params['framerate'] != first_params['framerate']:
                print(f"Warning: {filepath} has different sample rate. Results may vary.")
            
            if params['nchannels'] != first_params['nchannels']:
                print(f"Warning: {filepath} has different channels. Results may vary.")
            
            audio_data = self.read_audio_data(filepath)
            if audio_data:
                all_audio_data.append(audio_data)
                total_frames += params['nframes']
        
        if not all_audio_data:
            error_msg = "No valid audio data to merge"
            print(error_msg)
            if callback:
                callback(error_msg)
            return None
        
        # Determine output path
        if output_path is None:
            import time
            timestamp = int(time.time())
            output_path = os.path.join(
                Config.OUTPUT_DIR,
                f"merged_{timestamp}.wav"
            )
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if callback:
            callback("Merging audio files...")
        
        try:
            # Write merged file
            with wave.open(output_path, 'wb') as output_wav:
                output_wav.setnchannels(first_params['nchannels'])
                output_wav.setsampwidth(first_params['sampwidth'])
                output_wav.setframerate(first_params['framerate'])
                
                # Write all audio data
                for audio_data in all_audio_data:
                    output_wav.writeframes(audio_data)
            
            if callback:
                callback(f"Merged audio saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            error_msg = f"Error writing merged file: {str(e)}"
            print(error_msg)
            if callback:
                callback(error_msg)
            return None
    
    def merge_with_silence(
        self,
        input_files: List[str],
        silence_duration: float = 1.0,
        output_path: Optional[str] = None,
        callback: Optional[callable] = None
    ) -> Optional[str]:
        """
        Merge audio files with silence between them
        
        Args:
            input_files: List of audio file paths
            silence_duration: Duration of silence between files in seconds
            output_path: Output path
            callback: Progress callback
            
        Returns:
            Path to merged file or None
        """
        if not input_files:
            return None
        
        if len(input_files) == 1:
            return input_files[0]
        
        # Generate silence audio
        first_params = self.get_audio_params(input_files[0])
        if not first_params:
            return None
        
        # Create silence data
        silence_samples = int(first_params['framerate'] * silence_duration)
        silence_data = b'\x00' * (silence_samples * first_params['nchannels'] * first_params['sampwidth'])
        
        # Interleave files with silence
        files_with_silence = []
        for i, filepath in enumerate(input_files):
            files_with_silence.append(filepath)
            if i < len(input_files) - 1:  # Don't add silence after last file
                # Create temporary silence file
                silence_path = os.path.join(Config.OUTPUT_DIR, f"silence_{i}.wav")
                try:
                    with wave.open(silence_path, 'wb') as wav_file:
                        wav_file.setnchannels(first_params['nchannels'])
                        wav_file.setsampwidth(first_params['sampwidth'])
                        wav_file.setframerate(first_params['framerate'])
                        wav_file.writeframes(silence_data)
                    files_with_silence.append(silence_path)
                except Exception as e:
                    print(f"Error creating silence file: {e}")
        
        # Merge all files
        result = self.merge_files(files_with_silence, output_path, callback)
        
        # Clean up temporary silence files
        for i in range(len(input_files) - 1):
            silence_path = os.path.join(Config.OUTPUT_DIR, f"silence_{i}.wav")
            try:
                if os.path.exists(silence_path):
                    os.remove(silence_path)
            except Exception as e:
                print(f"Error removing silence file: {e}")
        
        return result
