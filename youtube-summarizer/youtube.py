import os
import subprocess
import whisper
import ssl
import urllib.request
import imageio_ffmpeg as ffmpeg
import re
import time
import yt_dlp
import sys

# Function to convert YouTube Shorts URL to standard URL
def convert_shorts_url(url):
    if "youtube.com/shorts/" in url:
        return re.sub(r"/shorts/", "/watch?v=", url)
    return url

# Function to download audio from YouTube with yt-dlp
def download_audio(youtube_url, output_path="audio.mp3"):
    try:
        print("Attempting to download audio from YouTube using yt-dlp...")
        # Remove existing audio file to avoid confusion
        if os.path.exists(output_path):
            os.remove(output_path)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path.replace('.mp3', '') + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'nocheckcertificate': True,  # Bypass SSL certificate verification
            'ffmpeg_location': ffmpeg.get_ffmpeg_exe(),  # Provide ffmpeg location from imageio_ffmpeg
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        print(f"Audio successfully downloaded as {output_path}")
        return True
    except Exception as e:
        print(f"An error occurred while downloading audio: {e}")
        return False

# Function to transcribe audio using whisper
def transcribe_audio(audio_path):
    try:
        print("Attempting to transcribe audio using Whisper...")
        # Add ffmpeg to PATH
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
        print(f"Using ffmpeg located at: {ffmpeg_path}")
        os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
        os.environ["FFMPEG_BINARY"] = ffmpeg_path  # Set FFMPEG_BINARY environment variable explicitly
        whisper.audio.FFMPEG = ffmpeg_path  # Set ffmpeg path directly in whisper's audio module
        # Convert audio to WAV format to ensure compatibility
        wav_path = "youtube_audio.wav"
        if os.path.exists(wav_path):
            os.remove(wav_path)
        subprocess.run([ffmpeg_path, "-i", audio_path, wav_path], check=True)
        # Load whisper model
        model = whisper.load_model("base")
        # Transcribe audio
        result = model.transcribe(wav_path, fp16=False)  # Ensure FP16 is not used on CPU
        print("Transcription:")
        print(result["text"])
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        print(f"FFmpeg path: {ffmpeg_path}")
        print("Checking if ffmpeg is accessible as a file or directory...")
        if not os.path.isfile(ffmpeg_path):
            print(f"Error: The ffmpeg path '{ffmpeg_path}' is not a valid file. Please verify the ffmpeg installation.")

if __name__ == "__main__":
    # Get YouTube URL from the user
    youtube_url = "https://www.youtube.com/watch?v=b4TpO9pYpqk"

    # Convert Shorts URL to standard URL if needed
    youtube_url = convert_shorts_url(youtube_url)

    # Download audio from YouTube
    audio_output_path = "youtube_audio.mp3.mp3" if os.path.exists("youtube_audio.mp3.mp3") else "youtube_audio.mp3"
    if download_audio(youtube_url, audio_output_path.split('.mp3')[0]):
        # Check if ffmpeg is installed
        try:
            ffmpeg_path = ffmpeg.get_ffmpeg_version()
            print("ffmpeg is installed and ready to use.")
        except Exception:
            print("Error: ffmpeg is not installed. Please install ffmpeg to proceed.")
            exit()

        # Transcribe the downloaded audio
        if os.path.exists(audio_output_path):
            transcribe_audio(audio_output_path)
        else:
            print("Error: Audio file not found. Unable to transcribe.")
