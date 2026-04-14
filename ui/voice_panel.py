"""
Voice Panel - TTS Voice Generation with Preview and Regeneration
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os

from core.tts_engine import TTSEngine
from core.config import Config


class VoicePanel(ttk.Frame):
    """Panel for voice generation with preview, regenerate, and custom prompt features"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.tts_engine = TTSEngine()
        self.current_output_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the voice panel UI"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text input section
        text_frame = ttk.LabelFrame(main_frame, text="Text to Convert")
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.text_input = tk.Text(text_frame, height=6, wrap=tk.WORD)
        self.text_input.pack(fill=tk.X, padx=5, pady=5)
        
        # Voice prompt section
        prompt_frame = ttk.LabelFrame(main_frame, text="Voice Prompt (Custom)")
        prompt_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(prompt_frame, text="Describe the voice you want:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        self.prompt_input = ttk.Entry(prompt_frame)
        self.prompt_input.pack(fill=tk.X, padx=5, pady=5)
        self.prompt_input.insert(0, "A clear, professional narrator voice")
        
        # Model selection
        model_frame = ttk.LabelFrame(main_frame, text="Model")
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.model_combo = ttk.Combobox(model_frame, state="readonly")
        self.model_combo.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_btn = ttk.Button(model_frame, text="Refresh Models", command=self.refresh_models)
        refresh_btn.pack(padx=5, pady=5)
        
        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.generate_btn = ttk.Button(btn_frame, text="Generate Speech", command=self.generate_speech)
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        self.preview_btn = ttk.Button(btn_frame, text="Preview Voice", command=self.preview_voice)
        self.preview_btn.pack(side=tk.LEFT, padx=5)
        
        self.regenerate_btn = ttk.Button(btn_frame, text="Regenerate", command=self.regenerate_speech)
        self.regenerate_btn.pack(side=tk.LEFT, padx=5)
        self.regenerate_btn['state'] = 'disabled'
        
        # Status and output
        status_frame = ttk.LabelFrame(main_frame, text="Status & Output")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.output_label = ttk.Label(status_frame, text="No output yet", wraplength=400)
        self.output_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Audio player placeholder (can be enhanced with actual audio player)
        player_frame = ttk.Frame(status_frame)
        player_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.play_btn = ttk.Button(player_frame, text="Play Audio", command=self.play_audio)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        self.play_btn['state'] = 'disabled'
        
        self.save_btn = ttk.Button(player_frame, text="Save As...", command=self.save_audio)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.save_btn['state'] = 'disabled'
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Initialize models list
        self.refresh_models()
    
    def refresh_models(self):
        """Refresh available models from LM Studio"""
        def on_models_fetched(models):
            self.model_combo['values'] = models
            if models:
                self.model_combo.current(0)
        
        self.tts_engine.fetch_models_async(callback=on_models_fetched)
    
    def update_status(self, message: str, is_error: bool = False):
        """Update status label"""
        self.status_label.config(text=message, foreground="red" if is_error else "green")
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        if loading:
            self.progress.start()
            self.generate_btn['state'] = 'disabled'
            self.preview_btn['state'] = 'disabled'
        else:
            self.progress.stop()
            self.generate_btn['state'] = 'normal'
            self.preview_btn['state'] = 'normal'
    
    def generate_speech(self):
        """Generate speech from text"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to convert")
            return
        
        voice_prompt = self.prompt_input.get().strip()
        if not voice_prompt:
            voice_prompt = "A clear, professional narrator voice"
        
        selected_model = self.model_combo.get()
        if selected_model:
            self.tts_engine.current_model = selected_model
        
        def on_progress(message: str):
            self.update_status(message)
        
        def on_complete(output_path: str):
            self.set_loading(False)
            if output_path:
                self.current_output_path = output_path
                self.output_label.config(text=f"Output: {output_path}")
                self.update_status("Generation complete!")
                self.regenerate_btn['state'] = 'normal'
                self.play_btn['state'] = 'normal'
                self.save_btn['state'] = 'normal'
            else:
                self.update_status("Generation failed", is_error=True)
        
        self.set_loading(True)
        self.update_status("Starting generation...")
        
        # Run in background thread
        thread = threading.Thread(
            target=lambda: on_complete(
                self.tts_engine.generate_speech(
                    text=text,
                    voice_prompt=voice_prompt,
                    callback=on_progress
                )
            ),
            daemon=True
        )
        thread.start()
    
    def regenerate_speech(self):
        """Regenerate speech with same or modified parameters"""
        if not self.current_output_path:
            messagebox.showwarning("Warning", "No previous generation to regenerate")
            return
        
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to regenerate")
            return
        
        voice_prompt = self.prompt_input.get().strip()
        
        def on_progress(message: str):
            self.update_status(message)
        
        def on_complete(output_path: str):
            self.set_loading(False)
            if output_path:
                self.current_output_path = output_path
                self.output_label.config(text=f"Output: {output_path} (regenerated)")
                self.update_status("Regeneration complete!")
            else:
                self.update_status("Regeneration failed", is_error=True)
        
        self.set_loading(True)
        self.update_status("Regenerating...")
        
        thread = threading.Thread(
            target=lambda: on_complete(
                self.tts_engine.regenerate_speech(
                    previous_output_path=self.current_output_path,
                    text=text,
                    voice_prompt=voice_prompt,
                    callback=on_progress
                )
            ),
            daemon=True
        )
        thread.start()
    
    def preview_voice(self):
        """Preview voice with sample text"""
        voice_prompt = self.prompt_input.get().strip()
        if not voice_prompt:
            voice_prompt = "A clear, professional narrator voice"
        
        def on_progress(message: str):
            self.update_status(message)
        
        def on_complete(output_path: str):
            self.set_loading(False)
            if output_path:
                self.update_status("Preview generated! Check voices/preview_sample.wav")
                # Try to play automatically
                try:
                    import subprocess
                    subprocess.call(['aplay', output_path])
                except:
                    pass
            else:
                self.update_status("Preview failed", is_error=True)
        
        self.set_loading(True)
        self.update_status("Generating preview...")
        
        thread = threading.Thread(
            target=lambda: on_complete(
                self.tts_engine.preview_voice(
                    voice_prompt=voice_prompt,
                    callback=on_progress
                )
            ),
            daemon=True
        )
        thread.start()
    
    def play_audio(self):
        """Play the generated audio"""
        if not self.current_output_path:
            return
        
        try:
            import subprocess
            subprocess.call(['aplay', self.current_output_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not play audio: {e}")
    
    def save_audio(self):
        """Save audio to a different location"""
        if not self.current_output_path:
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                import shutil
                shutil.copy2(self.current_output_path, filepath)
                messagebox.showinfo("Success", f"Audio saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
