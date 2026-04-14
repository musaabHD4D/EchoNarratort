# EchoNarrator

Professional Text-to-Speech and Audio Management Tool with LM Studio Integration.

## Features

### 🎤 Voice Generation
- Generate speech from text using LM Studio models
- **Voice Preview**: Listen to voice samples before generating full content
- **Regenerate**: Re-generate audio with modified prompts
- **Custom Prompts**: Edit voice generation prompts manually
- Background processing to prevent UI freezing

### 🤖 Model Management
- Remote LM Studio model management (Load/Unload)
- Automatic model list fetching from server
- Background threading for all operations
- Comprehensive error handling with clear user messages
- Real-time connection status monitoring

### 🔀 Audio Merger
- Merge multiple WAV audio files into one
- Add silence between merged files (optional)
- Reorder files before merging
- Fixed and improved merging algorithm

## Project Structure

```
EchoNarratort/
├── main.py              # Application entry point
├── core/                # Core business logic
│   ├── __init__.py
│   ├── config.py        # Configuration settings
│   ├── tts_engine.py    # Text-to-Speech engine
│   ├── model_manager.py # LM Studio model management
│   └── audio_merger.py  # Audio file merger
├── ui/                  # User interface components
│   ├── __init__.py
│   ├── main_window.py   # Main application window
│   ├── voice_panel.py   # Voice generation panel
│   ├── model_panel.py   # Model management panel
│   └── merger_panel.py  # Audio merger panel
├── voices/              # Generated voice previews
├── output/              # Generated audio files
├── projects/            # Project files
└── assets/              # Application assets
```

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- requests library

## Installation

1. Install required dependencies:
```bash
pip install requests
```

2. Make sure LM Studio is running with API server enabled on `localhost:1234`

3. Run the application:
```bash
python main.py
```

## Usage

### Voice Generation
1. Enter your text in the "Text to Convert" box
2. Customize the voice prompt (optional)
3. Select a model from the dropdown
4. Click "Generate Speech"
5. Use "Preview Voice" to test voice characteristics
6. Use "Regenerate" to re-generate with modified settings

### Model Management
1. Go to the "Model Manager" tab
2. Click "Check Connection" to verify LM Studio connection
3. Click "Refresh List" to fetch available models
4. Double-click a model or select and click "Load Selected"
5. Use "Unload Model" to free up resources

### Audio Merger
1. Go to the "Audio Merger" tab
2. Click "Add Files" to select audio files
3. Use arrow buttons to reorder files
4. Optionally enable "Add silence between files"
5. Click "Merge Files"
6. Use "Play Result" to listen to the merged audio

## Configuration

Edit `core/config.py` to customize:
- LM Studio host and port
- Default directories
- Audio settings

## Troubleshooting

### Cannot connect to LM Studio
- Ensure LM Studio is running
- Verify the API server is enabled in LM Studio settings
- Check that the port is set to 1234 (or update config)

### Model loading fails
- Ensure you have enough RAM for the model
- Try unloading other models first
- Check LM Studio logs for errors

### Audio merge fails
- Ensure all input files are valid WAV files
- Check that files are not corrupted
- Verify write permissions in output directory

## License

MIT License

## Author

Developed as a professional TTS and audio management solution.
