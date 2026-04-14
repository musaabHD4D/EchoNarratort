"""
Model Panel - LM Studio Model Management
Handles remote model loading/unloading with background threads
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from core.model_manager import ModelManager, ModelStatus


class ModelPanel(ttk.Frame):
    """Panel for managing LM Studio models remotely"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.model_manager = ModelManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the model management UI"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection status
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.connection_label = ttk.Label(status_frame, text="Checking...", foreground="orange")
        self.connection_label.pack(anchor=tk.W, padx=5, pady=5)
        
        check_btn = ttk.Button(status_frame, text="Check Connection", command=self.check_connection)
        check_btn.pack(padx=5, pady=5)
        
        # Model list
        list_frame = ttk.LabelFrame(main_frame, text="Available Models")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.models_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set)
        self.models_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.models_listbox.yview)
        
        # Bind double-click to load model
        self.models_listbox.bind('<Double-Button-1>', self.on_model_double_click)
        
        # Model actions
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_btn = ttk.Button(action_frame, text="Refresh List", command=self.refresh_models)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_btn = ttk.Button(action_frame, text="Load Selected", command=self.load_selected_model)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.unload_btn = ttk.Button(action_frame, text="Unload Model", command=self.unload_model)
        self.unload_btn.pack(side=tk.LEFT, padx=5)
        self.unload_btn['state'] = 'disabled'
        
        # Current model info
        info_frame = ttk.LabelFrame(main_frame, text="Current Model")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.current_model_label = ttk.Label(info_frame, text="No model loaded", foreground="gray")
        self.current_model_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.status_label = ttk.Label(info_frame, text="Status: Not Loaded", foreground="gray")
        self.status_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Progress indicator
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Initial connection check
        self.check_connection()
    
    def update_status(self, message: str, is_error: bool = False):
        """Update status label"""
        self.status_label.config(text=message, foreground="red" if is_error else "green")
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        if loading:
            self.progress.start()
            self.load_btn['state'] = 'disabled'
            self.unload_btn['state'] = 'disabled'
        else:
            self.progress.stop()
            self.update_buttons_state()
    
    def update_buttons_state(self):
        """Update button states based on current status"""
        status = self.model_manager.get_status()
        has_selection = self.models_listbox.curselection()
        
        if status == ModelStatus.LOADED:
            self.unload_btn['state'] = 'normal'
            self.load_btn['state'] = 'disabled'
        elif has_selection:
            self.load_btn['state'] = 'normal'
            self.unload_btn['state'] = 'disabled'
        else:
            self.load_btn['state'] = 'disabled'
            self.unload_btn['state'] = 'disabled'
    
    def check_connection(self):
        """Check LM Studio connection"""
        is_connected = self.model_manager.check_connection()
        
        if is_connected:
            self.connection_label.config(text="Connected to LM Studio", foreground="green")
            self.refresh_models()
        else:
            self.connection_label.config(
                text="Cannot connect to LM Studio. Make sure it's running on localhost:1234",
                foreground="red"
            )
            self.models_listbox.delete(0, tk.END)
            self.models_listbox.insert(tk.END, "No connection - start LM Studio first")
    
    def refresh_models(self):
        """Refresh available models list"""
        def on_models_fetched(models):
            self.models_listbox.delete(0, tk.END)
            
            if not models:
                self.models_listbox.insert(tk.END, "No models available")
            else:
                for model in models:
                    self.models_listbox.insert(tk.END, model)
            
            self.update_buttons_state()
        
        self.set_loading(True)
        self.model_manager.fetch_models_async(callback=on_models_fetched)
        self.set_loading(False)
    
    def on_model_double_click(self, event):
        """Handle double-click on model list"""
        self.load_selected_model()
    
    def load_selected_model(self):
        """Load selected model"""
        selection = self.models_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model first")
            return
        
        model_id = self.models_listbox.get(selection[0])
        
        def on_load_complete(success: bool, message: str):
            self.set_loading(False)
            if success:
                self.current_model_label.config(text=f"Loaded: {model_id}", foreground="green")
                self.update_status(message)
                self.update_buttons_state()
            else:
                self.update_status(message, is_error=True)
                messagebox.showerror("Error", message)
        
        self.set_loading(True)
        self.update_status(f"Loading model: {model_id}...")
        
        self.model_manager.load_model_async(model_id, callback=on_load_complete)
    
    def unload_model(self):
        """Unload current model"""
        def on_unload_complete(success: bool, message: str):
            self.set_loading(False)
            if success:
                self.current_model_label.config(text="No model loaded", foreground="gray")
                self.update_status(message)
                self.update_buttons_state()
            else:
                self.update_status(message, is_error=True)
                messagebox.showerror("Error", message)
        
        self.set_loading(True)
        self.update_status("Unloading model...")
        
        self.model_manager.unload_model_async(callback=on_unload_complete)
