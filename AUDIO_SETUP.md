# Audio/Video Support Setup for Gork Bot

Gork now supports listening to and transcribing audio/video files! Users can attach .mp3, .wav, and .mp4 files to messages that mention the bot, and Gork will automatically transcribe the audio content.

## Setup Instructions

### 1. Install System Dependencies

#### For Windows:
1. Install FFmpeg:
   - Download from https://ffmpeg.org/download.html
   - Add FFmpeg to your system PATH
   - Or use chocolatey: `choco install ffmpeg`

#### For Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

#### For macOS:
```bash
brew install ffmpeg
```

### 2. Install Python Dependencies

Run the following command to install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `pydub>=0.25.1` - Audio processing library
- `SpeechRecognition>=3.10.0` - Speech recognition library
- `moviepy>=1.0.3` - Video processing library
- `openai-whisper>=20231117` - OpenAI's Whisper model for transcription

### 3. First Run

When you first start the bot after installing these dependencies, it will automatically download the Whisper "base" model (about 142MB). This only happens once.

### 4. Restart the Bot

Restart your bot to load the new audio processing capabilities.

## Usage

Once configured, users can:

1. **Attach audio files** (.mp3, .wav) to messages that mention the bot
2. **Attach video files** (.mp4) to messages that mention the bot - audio will be extracted and transcribed
3. **Combine with text** - users can attach audio/video files along with text questions

### Examples:

- Attach a voice memo (.mp3) and mention the bot: "Hey @Gork, what do you think about this recording?"
- Attach a video file (.mp4) and ask: "@Gork can you transcribe what's being said in this video?"
- Just attach an audio file without text - Gork will automatically transcribe it

## Features

- **Automatic transcription** using OpenAI's Whisper model
- **Multiple format support**: .mp3, .wav, .mp4
- **File size limits**: 50MB maximum for audio/video files
- **Error handling**: Graceful fallbacks if transcription fails
- **Video audio extraction**: Automatically extracts audio from .mp4 files

## Troubleshooting

### Common Issues:

1. **"Whisper model not loaded" error**:
   - Make sure you have internet connection for the initial model download
   - Check that you have enough disk space (about 500MB for models)
   - Restart the bot after installing dependencies

2. **"FFmpeg not found" error**:
   - Make sure FFmpeg is installed and in your system PATH
   - Try reinstalling FFmpeg

3. **Audio transcription fails**:
   - Check that the audio file contains speech
   - Ensure the file isn't corrupted
   - Try with a smaller file first

4. **File too large error**:
   - The bot has a 50MB limit for audio/video files
   - Try compressing your audio/video file

### Performance Notes:

- Transcription time depends on audio length and system performance
- The "base" Whisper model provides good accuracy for most use cases
- Processing happens locally on your server (no external API calls for transcription)

## Status Check

Use the `/gork_status` command to verify that audio transcription is working:
- ✅ Audio/Video transcription (.mp3, .wav, .mp4) - Working
- ❌ Audio transcription (Whisper not loaded) - Needs setup

## Privacy

All audio transcription happens locally using the Whisper model. No audio data is sent to external services for transcription.
