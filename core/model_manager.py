"""
Model Manager - Remote LM Studio Model Management
Handles loading/unloading models with background threading
"""

import os
import json
import threading
import requests
from typing import List, Optional, Callable, Dict
from enum import Enum

from .config import Config


class ModelStatus(Enum):
    """Model loading status"""
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    ERROR = "error"


class ModelManager:
    """Manage LM Studio models remotely with thread-safe operations"""
    
    def __init__(self):
        self.base_url = Config.LM_STUDIO_BASE_URL
        self.status = ModelStatus.NOT_LOADED
        self.current_model = None
        self.available_models = []
        self.model_cache = {}
        self._lock = threading.Lock()
        
    def fetch_models_async(self, callback: Optional[Callable[[List[str]], None]] = None) -> threading.Thread:
        """Fetch available models in background thread"""
        def _fetch():
            models = self.fetch_models()
            if callback:
                callback(models)
        
        thread = threading.Thread(target=_fetch, daemon=True)
        thread.start()
        return thread
    
    def fetch_models(self) -> List[str]:
        """Fetch available models from LM Studio synchronously"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            with self._lock:
                if 'data' in data:
                    self.available_models = [model['id'] for model in data['data']]
                    # Cache model info
                    for model in data['data']:
                        self.model_cache[model['id']] = model
                else:
                    self.available_models = []
                    
            return self.available_models
            
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to LM Studio. Make sure it's running."
            print(error_msg)
            with self._lock:
                self.status = ModelStatus.ERROR
            return []
        except requests.exceptions.Timeout:
            error_msg = "Connection timeout to LM Studio"
            print(error_msg)
            with self._lock:
                self.status = ModelStatus.ERROR
            return []
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching models: {str(e)}"
            print(error_msg)
            with self._lock:
                self.status = ModelStatus.ERROR
            return []
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {str(e)}"
            print(error_msg)
            with self._lock:
                self.status = ModelStatus.ERROR
            return []
    
    def load_model_async(
        self,
        model_id: str,
        callback: Optional[Callable[[bool, str], None]] = None
    ) -> threading.Thread:
        """Load model in background thread to prevent UI freezing"""
        def _load():
            with self._lock:
                self.status = ModelStatus.LOADING
            
            success, message = self.load_model(model_id)
            
            with self._lock:
                if success:
                    self.status = ModelStatus.LOADED
                    self.current_model = model_id
                else:
                    self.status = ModelStatus.ERROR
            
            if callback:
                callback(success, message)
        
        thread = threading.Thread(target=_load, daemon=True)
        thread.start()
        return thread
    
    def load_model(self, model_id: str) -> tuple:
        """
        Load a specific model in LM Studio
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not model_id:
            return False, "No model ID provided"
        
        try:
            response = requests.post(
                f"{self.base_url}/models/load",
                json={"model": model_id},
                timeout=60  # Loading can take time
            )
            response.raise_for_status()
            
            return True, f"Model '{model_id}' loaded successfully"
            
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to LM Studio"
        except requests.exceptions.Timeout:
            return False, "Model loading timed out"
        except requests.exceptions.HTTPError as e:
            return False, f"HTTP Error: {e.response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Error loading model: {str(e)}"
        except json.JSONDecodeError as e:
            return False, f"Invalid response from server"
    
    def unload_model_async(
        self,
        callback: Optional[Callable[[bool, str], None]] = None
    ) -> threading.Thread:
        """Unload current model in background thread"""
        def _unload():
            with self._lock:
                self.status = ModelStatus.UNLOADING
            
            success, message = self.unload_model()
            
            with self._lock:
                if success:
                    self.status = ModelStatus.NOT_LOADED
                    self.current_model = None
                else:
                    self.status = ModelStatus.ERROR
            
            if callback:
                callback(success, message)
        
        thread = threading.Thread(target=_unload, daemon=True)
        thread.start()
        return thread
    
    def unload_model(self) -> tuple:
        """
        Unload current model
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            response = requests.post(
                f"{self.base_url}/models/unload",
                timeout=30
            )
            response.raise_for_status()
            
            return True, "Model unloaded successfully"
            
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to LM Studio"
        except requests.exceptions.Timeout:
            return False, "Model unloading timed out"
        except requests.exceptions.RequestException as e:
            return False, f"Error unloading model: {str(e)}"
    
    def get_status(self) -> ModelStatus:
        """Get current model status"""
        with self._lock:
            return self.status
    
    def get_current_model(self) -> Optional[str]:
        """Get currently loaded model ID"""
        with self._lock:
            return self.current_model
    
    def is_loaded(self) -> bool:
        """Check if a model is currently loaded"""
        with self._lock:
            return self.status == ModelStatus.LOADED and self.current_model is not None
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        with self._lock:
            return self.available_models.copy()
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get detailed info about a specific model"""
        with self._lock:
            return self.model_cache.get(model_id)
    
    def check_connection(self) -> bool:
        """Check if LM Studio is reachable"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except:
            return False
