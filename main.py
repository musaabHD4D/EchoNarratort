"""
EchoNarrator - Advanced Text-to-Speech and AI Model Management System
Main Entry Point
"""

import sys
import os

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from ui.main_window import EchoNarratorApp

if __name__ == "__main__":
    app = EchoNarratorApp()
    app.run()
