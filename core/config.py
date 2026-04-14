"""
Configuration settings for EchoNarrator
"""

import os

class Config:
    """Application configuration"""
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VOICES_DIR = os.path.join(BASE_DIR, 'voices')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    PROJECTS_DIR = os.path.join(BASE_DIR, 'projects')
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    
    # LM Studio API
    LM_STUDIO_HOST = "localhost"
    LM_STUDIO_PORT = 1234
    LM_STUDIO_BASE_URL = f"http://{LM_STUDIO_HOST}:{LM_STUDIO_PORT}/v1"
    
    # Audio settings
    DEFAULT_SAMPLE_RATE = 22050
    DEFAULT_FORMAT = "wav"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for directory in [cls.VOICES_DIR, cls.OUTPUT_DIR, cls.PROJECTS_DIR, cls.ASSETS_DIR]:
            os.makedirs(directory, exist_ok=True)
