"""
Text-to-Speech Engine with LM Studio Integration
Supports voice preview, regeneration, and custom prompts
"""

import os
import json
import time
import threading
import requests
from typing import Optional, List, Dict, Callable
from pathlib import Path

from .config import Config


class TTSEngine:
    """Advanced TTS Engine with LM Studio integration"""
    
    def __init__(self):
        self.base_url = Config.LM_STUDIO_BASE_URL
        self.current_model = None
        self.available_models = []
        self.voices_cache = {}
        
    def fetch_models(self) -> List[str]:
        """Fetch available models from LM Studio"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data:
                self.available_models = [model['id'] for model in data['data']]
            else:
                self.available_models = []
                
            return self.available_models
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}")
            self.available_models = []
            return []
    
    def load_model(self, model_id: str) -> bool:
        """Load a specific model in LM Studio"""
        try:
            response = requests.post(
                f"{self.base_url}/models/load",
                json={"model": model_id},
                timeout=30
            )
            response.raise_for_status()
            self.current_model = model_id
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error loading model: {e}")
            return False
    
    def unload_model(self) -> bool:
        """Unload current model"""
        try:
            response = requests.post(
                f"{self.base_url}/models/unload",
                timeout=10
            )
            response.raise_for_status()
            self.current_model = None
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error unloading model: {e}")
            return False
    
    def generate_speech(
        self,
        text: str,
        voice_prompt: Optional[str] = None,
        output_path: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """
        Generate speech from text
        
        Args:
            text: Text to convert to speech
            voice_prompt: Custom prompt for voice generation
            output_path: Path to save the audio file
            callback: Optional callback for progress updates
            
        Returns:
            Path to generated audio file or None if failed
        """
        if callback:
            callback("Generating speech...")
        
        # Default voice prompt if not provided
        if not voice_prompt:
            voice_prompt = "A clear, professional narrator voice"
        
        # Prepare request payload
        payload = {
            "model": self.current_model or "default",
            "prompt": text,
            "voice_settings": {
                "prompt": voice_prompt
            },
            "stream": False
        }
        
        try:
            if callback:
                callback("Sending request to TTS server...")
            
            response = requests.post(
                f"{self.base_url}/audio/speech",
                json=payload,
                timeout=60,
                stream=True
            )
            response.raise_for_status()
            
            # Determine output path
            if output_path is None:
                timestamp = int(time.time())
                output_path = os.path.join(
                    Config.OUTPUT_DIR,
                    f"speech_{timestamp}.wav"
                )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if callback:
                callback("Saving audio file...")
            
            # Save audio content
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if callback:
                callback(f"Audio saved to: {output_path}")
            
            return output_path
            
        except requests.exceptions.RequestException as e:
            error_msg = f"TTS generation failed: {str(e)}"
            print(error_msg)
            if callback:
                callback(error_msg)
            return None
    
    def regenerate_speech(
        self,
        previous_output_path: str,
        text: str,
        voice_prompt: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Regenerate speech with same or modified parameters"""
        # Optionally backup previous file
        if os.path.exists(previous_output_path):
            backup_path = previous_output_path + ".bak"
            try:
                os.rename(previous_output_path, backup_path)
            except Exception as e:
                print(f"Could not backup previous file: {e}")
        
        # Generate new speech
        return self.generate_speech(
            text=text,
            voice_prompt=voice_prompt,
            output_path=previous_output_path,
            callback=callback
        )
    
    def preview_voice(
        self,
        voice_prompt: str,
        sample_text: str = "This is a voice preview sample.",
        callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Generate a quick voice preview"""
        preview_path = os.path.join(Config.VOICES_DIR, "preview_sample.wav")
        return self.generate_speech(
            text=sample_text,
            voice_prompt=voice_prompt,
            output_path=preview_path,
            callback=callback
        )
    
    def get_current_model(self) -> Optional[str]:
        """Get currently loaded model"""
        return self.current_model
    
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded"""
        return self.current_model is not None
    
    def fetch_models_async(self, callback: Callable[[List[str]], None]):
        """Fetch models asynchronously to prevent UI freezing"""
        def _fetch_thread():
            models = self.fetch_models()
            # Call callback in main thread context (tkinter safe)
            if hasattr(callback, '__call__'):
                # For tkinter, we need to schedule the callback
                import tkinter as tk
                root = tk._default_root
                if root:
                    root.after(0, lambda: callback(models))
                else:
                    callback(models)
        
        thread = threading.Thread(target=_fetch_thread, daemon=True)
        thread.start()
