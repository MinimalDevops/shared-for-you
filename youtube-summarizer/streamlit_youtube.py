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
import streamlit as st

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
        return result["text"]
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        print(f"FFmpeg path: {ffmpeg_path}")
        print("Checking if ffmpeg is accessible as a file or directory...")
        if not os.path.isfile(ffmpeg_path):
            print(f"Error: The ffmpeg path '{ffmpeg_path}' is not a valid file. Please verify the ffmpeg installation.")
        return None

# Streamlit app to summarize YouTube videos
def main():
    # Set the title and background color
    st.title("YouTube Video Summarizer 🎥")
    st.markdown('<style>h1{color: orange; text-align: center;}</style>', unsafe_allow_html=True)
    st.subheader('Built with Yt_dlp, Streamlit, and Whisper')
    st.markdown('<style>h3{color: pink; text-align: center;}</style>', unsafe_allow_html=True)

    # Expander for app details
    with st.expander("About the App"):
        st.write("This app allows you to summarize the audio of a YouTube video.")
        st.write("Enter a YouTube URL in the input box below and click 'Submit' to start.")

    # Input box for YouTube URL
    youtube_url = st.text_input("Enter YouTube URL")

    # Submit button
    if st.button("Submit") and youtube_url:
        start_time = time.time()  # Start the timer

        # Convert Shorts URL to standard URL if needed
        youtube_url = convert_shorts_url(youtube_url)

        # Download audio from YouTube
        audio_output_path = "youtube_audio.mp3.mp3" if os.path.exists("youtube_audio.mp3.mp3") else "youtube_audio.mp3"
        if download_audio(youtube_url, audio_output_path.split('.mp3')[0]):
            # Transcribe the downloaded audio
            if os.path.exists(audio_output_path):
                output = transcribe_audio(audio_output_path)
                end_time = time.time()  # End the timer
                elapsed_time = end_time - start_time

                # Display layout with 2 columns
                col1, col2 = st.columns([1, 1])

                # Column 1: Video view
                with col1:
                    st.video(youtube_url)

                # Column 2: Summary View
                with col2:
                    st.header("Summarization of YouTube Video")
                    if output:
                        st.write(output)
                    st.write(f"Time taken: {elapsed_time:.2f} seconds")
            else:
                st.error("Error: Audio file not found. Unable to transcribe.")
        else:
            st.error("Error: Unable to download audio from YouTube.")

if __name__ == "__main__":
    main()
