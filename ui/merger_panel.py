"""
Audio Merger Panel - Merge multiple audio files
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os

from core.audio_merger import AudioMerger
from core.config import Config


class MergerPanel(ttk.Frame):
    """Panel for merging multiple audio files"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.audio_merger = AudioMerger()
        self.input_files = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the merger panel UI"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input files section
        files_frame = ttk.LabelFrame(main_frame, text="Input Files")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # File list with scrollbar
        list_container = ttk.Frame(files_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)
        
        # File management buttons
        file_btn_frame = ttk.Frame(files_frame)
        file_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        add_btn = ttk.Button(file_btn_frame, text="Add Files", command=self.add_files)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = ttk.Button(file_btn_frame, text="Remove Selected", command=self.remove_selected)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(file_btn_frame, text="Clear All", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        move_up_btn = ttk.Button(file_btn_frame, text="↑", command=self.move_up)
        move_up_btn.pack(side=tk.LEFT, padx=5)
        
        move_down_btn = ttk.Button(file_btn_frame, text="↓", command=self.move_down)
        move_down_btn.pack(side=tk.LEFT, padx=5)
        
        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Merge Options")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.silence_var = tk.BooleanVar(value=False)
        silence_check = ttk.Checkbutton(
            options_frame,
            text="Add silence between files (seconds):",
            variable=self.silence_var,
            command=self.toggle_silence_option
        )
        silence_check.pack(anchor=tk.W, padx=5, pady=5)
        
        self.silence_duration = ttk.Spinbox(options_frame, from_=0.1, to=10.0, increment=0.1, width=10)
        self.silence_duration.set(1.0)
        self.silence_duration.pack(anchor=tk.W, padx=20, pady=5)
        self.silence_duration['state'] = 'disabled'
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        browse_btn = ttk.Button(output_frame, text="Browse...", command=self.browse_output)
        browse_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.merge_btn = ttk.Button(action_frame, text="Merge Files", command=self.merge_files)
        self.merge_btn.pack(side=tk.LEFT, padx=5)
        
        self.play_btn = ttk.Button(action_frame, text="Play Result", command=self.play_result)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        self.play_btn['state'] = 'disabled'
        
        # Status and progress
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        self.result_label = ttk.Label(status_frame, text="", wraplength=400)
        self.result_label.pack(anchor=tk.W, padx=5, pady=5)
    
    def toggle_silence_option(self):
        """Toggle silence duration input"""
        if self.silence_var.get():
            self.silence_duration['state'] = 'normal'
        else:
            self.silence_duration['state'] = 'disabled'
    
    def add_files(self):
        """Add audio files to merge"""
        filetypes = [
            ("WAV files", "*.wav"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(title="Select Audio Files", filetypes=filetypes)
        
        if files:
            for filepath in files:
                if filepath not in self.input_files:
                    self.input_files.append(filepath)
                    self.files_listbox.insert(tk.END, os.path.basename(filepath))
            
            self.update_status(f"Added {len(files)} file(s)")
    
    def remove_selected(self):
        """Remove selected file from list"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to remove")
            return
        
        index = selection[0]
        self.input_files.pop(index)
        self.files_listbox.delete(index)
        
        self.update_status("File removed")
    
    def clear_all(self):
        """Clear all files"""
        self.input_files = []
        self.files_listbox.delete(0, tk.END)
        self.update_status("All files cleared")
    
    def move_up(self):
        """Move selected file up"""
        selection = self.files_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        # Swap in list
        self.input_files[index], self.input_files[index-1] = self.input_files[index-1], self.input_files[index]
        # Update listbox
        self.files_listbox.delete(index)
        self.files_listbox.insert(index-1, os.path.basename(self.input_files[index-1]))
        self.files_listbox.selection_clear(0, tk.END)
        self.files_listbox.selection_set(index-1)
    
    def move_down(self):
        """Move selected file down"""
        selection = self.files_listbox.curselection()
        if not selection or selection[0] == len(self.input_files) - 1:
            return
        
        index = selection[0]
        # Swap in list
        self.input_files[index], self.input_files[index+1] = self.input_files[index+1], self.input_files[index]
        # Update listbox
        self.files_listbox.delete(index)
        self.files_listbox.insert(index+1, os.path.basename(self.input_files[index+1]))
        self.files_listbox.selection_clear(0, tk.END)
        self.files_listbox.selection_set(index+1)
    
    def browse_output(self):
        """Browse for output file location"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if filepath:
            self.output_path_var.set(filepath)
    
    def update_status(self, message: str, is_error: bool = False):
        """Update status label"""
        self.status_label.config(text=message, foreground="red" if is_error else "green")
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        if loading:
            self.progress.start()
            self.merge_btn['state'] = 'disabled'
        else:
            self.progress.stop()
            self.merge_btn['state'] = 'normal'
    
    def merge_files(self):
        """Merge the selected audio files"""
        if not self.input_files:
            messagebox.showwarning("Warning", "Please add at least one file to merge")
            return
        
        if len(self.input_files) < 2:
            messagebox.showwarning("Warning", "Please add at least two files to merge")
            return
        
        output_path = self.output_path_var.get() if self.output_path_var.get() else None
        
        use_silence = self.silence_var.get()
        silence_duration = float(self.silence_duration.get()) if use_silence else 0.0
        
        def on_progress(message: str):
            self.update_status(message)
        
        def on_complete(result_path: str):
            self.set_loading(False)
            if result_path:
                self.result_path = result_path
                self.result_label.config(text=f"Merged: {result_path}")
                self.update_status("Merge complete!")
                self.play_btn['state'] = 'normal'
            else:
                self.update_status("Merge failed", is_error=True)
        
        self.set_loading(True)
        self.update_status("Starting merge...")
        
        if use_silence:
            thread = threading.Thread(
                target=lambda: on_complete(
                    self.audio_merger.merge_with_silence(
                        input_files=self.input_files,
                        silence_duration=silence_duration,
                        output_path=output_path,
                        callback=on_progress
                    )
                ),
                daemon=True
            )
        else:
            thread = threading.Thread(
                target=lambda: on_complete(
                    self.audio_merger.merge_files(
                        input_files=self.input_files,
                        output_path=output_path,
                        callback=on_progress
                    )
                ),
                daemon=True
            )
        
        thread.start()
    
    def play_result(self):
        """Play the merged result"""
        if not hasattr(self, 'result_path') or not self.result_path:
            return
        
        try:
            import subprocess
            subprocess.call(['aplay', self.result_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not play audio: {e}")
