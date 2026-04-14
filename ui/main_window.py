"""
Main Application Window - EchoNarrator
Tabbed interface for all features
"""

import tkinter as tk
from tkinter import ttk
import threading

from core.config import Config
from ui.voice_panel import VoicePanel
from ui.model_panel import ModelPanel
from ui.merger_panel import MergerPanel


class EchoNarratorApp:
    """Main application class for EchoNarrator"""
    
    def __init__(self):
        # Ensure directories exist
        Config.ensure_directories()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("EchoNarrator - Professional TTS & Audio Tool")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Setup styles
        self.setup_styles()
        
        # Create menu
        self.create_menu()
        
        # Create main UI
        self.create_main_ui()
        
        # Status bar
        self.create_status_bar()
    
    def setup_styles(self):
        """Setup application styles"""
        style = ttk.Style()
        
        # Try to use a modern theme
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Status.TLabel', font=('Helvetica', 10))
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_ui(self):
        """Create the main tabbed interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(
            main_container,
            text="🎙️ EchoNarrator",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 10))
        
        # Tab control
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Voice Generation Tab
        self.voice_panel = VoicePanel(self.notebook)
        self.notebook.add(self.voice_panel, text="🎤 Voice Generation")
        
        # Model Management Tab
        self.model_panel = ModelPanel(self.notebook)
        self.notebook.add(self.model_panel, text="🤖 Model Manager")
        
        # Audio Merger Tab
        self.merger_panel = MergerPanel(self.notebook)
        self.notebook.add(self.merger_panel, text="🔀 Audio Merger")
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready - LM Studio should be running on localhost:1234",
            style='Status.TLabel',
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.config(text=message)
    
    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About EchoNarrator")
        about_window.geometry("400x200")
        about_window.resizable(False, False)
        
        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()
        
        content = ttk.Frame(about_window, padding=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            content,
            text="EchoNarrator",
            font=('Helvetica', 18, 'bold')
        ).pack(pady=(0, 10))
        
        ttk.Label(
            content,
            text="Professional Text-to-Speech & Audio Tool",
            font=('Helvetica', 11)
        ).pack(pady=(0, 20))
        
        ttk.Label(
            content,
            text="Version 2.0\n\nFeatures:\n• Voice Generation with Preview\n• Model Management (LM Studio)\n• Audio File Merging\n• Background Processing",
            justify=tk.CENTER
        ).pack()
        
        ttk.Button(
            content,
            text="Close",
            command=about_window.destroy
        ).pack(pady=(20, 0))
    
    def run(self):
        """Run the application"""
        # Start connection check in background
        def check_connection():
            from core.model_manager import ModelManager
            manager = ModelManager()
            is_connected = manager.check_connection()
            
            if is_connected:
                self.update_status("Connected to LM Studio")
            else:
                self.update_status("Warning: LM Studio not detected on localhost:1234")
        
        threading.Thread(target=check_connection, daemon=True).start()
        
        # Start main loop
        self.root.mainloop()


if __name__ == "__main__":
    app = EchoNarratorApp()
    app.run()
