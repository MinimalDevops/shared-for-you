# Youtube Summarize

### Create the environment for python:
python3 -m venv youtube

### Activate it
source youtube/bin/activate 

### use pip to install the requirements
Requirements.txt has all the 

### Run the streamlit command to have it running:
streamlit run streamlit_youtube_summarizer.py


## Brief explanation of setup on Windows

## Run the llama with following command on windows

ollama run <model> 

Note: I am using llama 3.1 8b q8

## I am running private gpt with gpu using cuda support and I run it over the network so that I can access it over my connected mac device over LAN

* $env:PGPT_PROFILES="ollama"
* poetry run python -m uvicorn private_gpt.main:app --reload --port 8001 --host 0.0.0.0

## I ensure the privateGPT is accessible over browser using the endpoint. In my case, it is 172.16.1.10:8001


## Application Flow:

1. Streamlit runs the code and ask for youtube url from browser running at localhost.
2. Youtube library downloads the audio in mp3 format.
3. That is converted into wav format and used by whisper to transcribe it
4. The transcribed text is converted to pdf and ingested in PrivateGPT
5. PrivateGPT Api is invoked to summarize it.
6. Summary is received and printed by streamlit on the browser
7. The ingested doc is deleted from PrivateGPT