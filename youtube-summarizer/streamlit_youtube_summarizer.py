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
from fpdf import FPDF
import requests
import asyncio

# Base URL for summarizing
base_url = "http://172.16.1.10:8001"

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

# Function to create a PDF from transcribed text
def create_pdf(transcription, pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, transcription)
    if not os.path.exists(os.path.dirname(pdf_path)):
        os.makedirs(os.path.dirname(pdf_path))
    pdf.output(pdf_path)
    print(f"PDF created at {pdf_path}")

# Function to summarize the PDF
def summarize_pdf(pdf_path):
    print(f"Starting summarization for {pdf_path}")

    # Step 1: Ingest the PDF
    ingest_url = f"{base_url}/v1/ingest/file"
    with open(pdf_path, 'rb') as file:
        ingest_response = requests.post(ingest_url, files={'file': file})

    if ingest_response.status_code == 200:
        print(f"PDF {pdf_path} ingested successfully.")
    else:
        print(f"Failed to ingest PDF: {ingest_response.status_code}")
        return None

    # Step 2: Summarize the PDF
    summarize_url = f"{base_url}/v1/summarize"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "text": "string",
        "use_context": True,
        "prompt": ("Provide a comprehensive summary of the provided context information. "
                   "The summary should cover all the key points and main ideas presented in the original text, "
                   "while also condensing the information into a concise and easy-to-understand format. "
                   "Please ensure that the summary includes relevant details and examples that support the main ideas, "
                   "while avoiding any unnecessary information or repetition. Don't include any first line as heading."),
        "stream": False
    }

    try:
        response = requests.post(summarize_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error if the request failed
        summary = response.json().get("summary", "No summary found")
        print(f"Summary: {summary}")
        return summary
    except requests.exceptions.RequestException as e:
        print(f"Error during summarization: {e}")
        return None

# Function to delete the ingested PDF
def delete_ingested_document(pdf_name):
    list_url = f"{base_url}/v1/ingest/list"
    list_response = requests.get(list_url)

    if list_response.status_code == 200:
        list_data = list_response.json()
        doc_ids_to_delete = [
            document['doc_id']
            for document in list_data.get('data', [])
            if document['doc_metadata']['file_name'] == pdf_name
        ]

        for doc_id in doc_ids_to_delete:
            delete_url = f"{base_url}/v1/ingest/{doc_id}"
            delete_response = requests.delete(delete_url)

            if delete_response.status_code == 200:
                print(f"Document with doc_id {doc_id} successfully deleted.")
            else:
                print(f"Failed to delete document with doc_id {doc_id}: {delete_response.status_code}")
    else:
        print(f"Failed to fetch document list: {list_response.status_code}")

# Streamlit app to summarize YouTube videos
def main():
    # Set the title and background color
    st.title("YouTube Video Summarizer 🎥")
    st.markdown('<style>h1{color: orange; text-align: center;}</style>', unsafe_allow_html=True)
    #st.subheader('Built with Yt_dlp, Streamlit, Whisper, PrivateGPT, Ollama')
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
                if output:
                    # Create PDF from transcription
                    pdf_path = "pdf/youtube_transcription.pdf"
                    create_pdf(output, pdf_path)

                    # Summarize the PDF
                    summary = summarize_pdf(pdf_path)

                    # Display layout with 2 columns
                    col1, col2 = st.columns([1, 1])

                    # Column 1: Video view
                    with col1:
                        st.video(youtube_url)

                    # Column 2: Summary View
                    with col2:
                        st.header("Summarization of YouTube Video")
                        if summary:
                            st.write(summary)

                    # Delete the ingested document after summarization
                    delete_ingested_document(os.path.basename(pdf_path))
                    end_time = time.time()  # End the timer
                    elapsed_time = end_time - start_time
                    st.write(f"Time taken: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
