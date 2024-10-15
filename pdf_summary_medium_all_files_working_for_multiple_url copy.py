import os
import re
import asyncio
import subprocess
import requests
import time
from datetime import datetime
from pyppeteer import connect  # Import connect function

# Path to the sample PDF markdown content
SAMPLE_PDF_MD_PATH = 'samplefiles/pdf.md'

# Parameterize the base URL for summarizing
base_url = "http://172.16.1.10:8001"

# Logging configuration
ENABLE_LOGGING = True  # Set to False to disable logging to file
LOG_DIR = 'logs/'  # Directory where log files will be stored
log_file = None

# Set up logging file if logging is enabled
if ENABLE_LOGGING:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(LOG_DIR, f'log_{timestamp}.log')

def log_message(message):
    """Log a message to console and optionally to a file."""
    print(message)
    if ENABLE_LOGGING and log_file:
        with open(log_file, 'a') as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

async def download_pdf(url, pdf_name, pdf_dir, pdf_path):
    """Download the PDF from the URL and store it in the pdf directory relative to the markdown file."""
    log_message(f"Attempting to download PDF for URL: {url}")

    # Construct the full path for the PDF
    response = requests.get("http://localhost:9222/json/version")
    if response.status_code == 200:
        log_message("Connected to Chrome successfully")
    else:
        log_message(f"Failed to connect to Chrome: {response.status_code}")
        return

    ws_url = response.json()["webSocketDebuggerUrl"]
    log_message(f"WebSocket URL: {ws_url}")

    # Initialize browser connection
    browser = await connect(browserWSEndpoint=ws_url)
    browser_connected = True  # Flag to track if the browser is still connected

    try:
        # Check if the PDF already exists
        if os.path.exists(pdf_path):
            log_message(f"PDF already exists at {pdf_path}, skipping download.")
            # Ensure the browser is closed before summarizing
            await browser.close()
            browser_connected = False
            log_message("Browser closed as PDF already exists.")
            return

        # Proceed to download the PDF since it doesn't exist
        page = await browser.newPage()
        await page.goto(url)

        # Handle cookie consent popup if present
        try:
            log_message("Checking for cookie consent popup...")
            for _ in range(3):
                try:
                    await page.waitForSelector('button[aria-label="Accept all cookies"]', timeout=10000)
                    await page.click('button[aria-label="Accept all cookies"]')
                    log_message("Accepted cookies.")
                    break
                except Exception as e:
                    log_message(f"Retrying to accept cookies: {e}")
                    time.sleep(2)
        except Exception as e:
            log_message(f"Error handling cookie consent: {e}")

        # Scroll the page to the bottom and then back to the top
        log_message("Scrolling to the bottom of the page...")
        await auto_scroll(page)
        await page.evaluate('window.scrollTo(0, 0)')
        log_message("Scrolled back to the top of the page.")

        # Handle potential popups
        try:
            log_message("Checking for popups...")
            close_button_selectors = [
                '[aria-label="Close"]',
                '[class*="close"]',
                '[class*="popup-close"]',
                '[class*="dismiss"]',
                'button[aria-label="Dismiss"]',
                'button[aria-label="Close"]'
            ]
            for selector in close_button_selectors:
                elements = await page.querySelectorAll(selector)
                if elements:
                    for element in elements:
                        await element.click()
                        log_message(f"Popup closed using selector: {selector}")
                        break
        except Exception as e:
            log_message(f"Error handling popup: {e}")

        # Scroll the page to trigger lazy-loaded content
        await auto_scroll(page)

        # Ensure the PDF directory exists
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)

        # Generate the PDF and save it
        await page.pdf({'path': pdf_path, 'format': 'A4', 'printBackground': True})
        log_message(f"PDF generated at {pdf_path}")

    finally:
        # Ensure the browser is closed, even if an exception occurs or PDF already exists
        if browser_connected:
            try:
                log_message("Closing browser...")
                await browser.close()
            except Exception as e:
                log_message(f"Error while closing browser: {e}")

async def auto_scroll(page):
    """Function to scroll the page to trigger lazy loading."""
    await page.evaluate('''
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 100;
                let timer = setInterval(() => {
                    let scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;

                    if (totalHeight >= scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    ''')

def open_chrome_with_profile():
    """Open Chrome with a profile."""
    log_message("Opening Chrome with profile...")
    subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 
                      '--remote-debugging-port=9222', '--profile-directory=Profile 2'])
    time.sleep(2)

def summarize_pdf_and_update_md(pdf_path, md_file, url):
    """Summarize the PDF and update the markdown file."""
    log_message(f"Starting summarization for {pdf_path}")

    # Step 1: Ingest the PDF
    ingest_url = f"{base_url}/v1/ingest/file"
    with open(pdf_path, 'rb') as file:
        ingest_response = requests.post(ingest_url, files={'file': file})

    if ingest_response.status_code == 200:
        log_message(f"PDF {pdf_path} ingested successfully.")
    else:
        log_message(f"Failed to ingest PDF: {ingest_response.status_code}")
        return

    # Step 2: Summarize the PDF
    summarize_url = f"{base_url}/v1/summarize"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "text": "string",
        "use_context": True,
        "prompt": ("Provide a comprehensive summary of the provided context information in 50 words. "
                   "The summary should cover all the key points and main ideas presented in the original text, "
                   "while also condensing the information into a concise and easy-to-understand format. "
                   "Please ensure that the summary includes relevant details and examples that support the main ideas, "
                   "while avoiding any unnecessary information or repetition. Don't include any first line as heading."),
        "stream": False
    }

    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            log_message(f"Sending summarization request (Attempt {attempt})...")
            response = requests.post(summarize_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error if the request failed
            summary = response.json().get("summary", "No summary found")
            log_message(f"Summary: {summary}")
            break
        except requests.exceptions.RequestException as e:
            log_message(f"Error during summarization attempt {attempt}: {e}")
            if attempt < max_attempts:
                log_message("Retrying after 10 seconds...")
                time.sleep(10)
            else:
                log_message("All summarization attempts failed. Skipping this PDF.")
                return

    # Step 3: Generate PDF and summary content
    with open(SAMPLE_PDF_MD_PATH, 'r') as sample_file:
        pdf_content = sample_file.read().replace("Name.pdf", f"{os.path.basename(pdf_path)}")
        pdf_content = pdf_content.replace("summary", summary)

    # Step 4: Locate URL and insert generated content in the markdown file
    with open(md_file, 'r') as file:
        lines = file.readlines()

    url_pattern = re.compile(re.escape(url))
    for i, line in enumerate(lines):
        if url_pattern.search(line):
            lines.insert(i + 1, pdf_content + '\n')
            log_message(f"Inserted content after URL at line index: {i}")
            break

    # Write the updated content back to the markdown file
    with open(md_file, 'w') as file:
        file.writelines(lines)

    log_message(f"Markdown file {md_file} updated successfully.")

    # Step 5: Delete the ingested document
    delete_ingested_document(os.path.basename(pdf_path))

def delete_ingested_document(pdf_name):
    """Delete the ingested document based on its name."""
    list_url = f"{base_url}/v1/ingest/list"
    list_response = requests.get(list_url)

    if list_response.status_code == 200:
        list_data = list_response.json()
        doc_ids_to_delete = [
            document['doc_id']
            for document in list_data.get('data', [])
            if document['doc_metadata']['file_name'] == pdf_name
        ]

        if doc_ids_to_delete:
            log_message(f"Document IDs for deletion: {doc_ids_to_delete}")
        else:
            log_message(f"No Document IDs found for {pdf_name}.")
            return

        for doc_id in doc_ids_to_delete:
            delete_url = f"{base_url}/v1/ingest/{doc_id}"
            delete_response = requests.delete(delete_url)

            if delete_response.status_code == 200:
                log_message(f"Document with doc_id {doc_id} successfully deleted.")
            else:
                log_message(f"Failed to delete document with doc_id {doc_id}: {delete_response.status_code}")
    else:
        log_message(f"Failed to fetch document list: {list_response.status_code}")

def process_markdown(md_path):
    """Process a markdown file and download PDFs."""
    log_message(f"Processing markdown file: {md_path}")

    with open(md_path, 'r') as file:
        lines = file.readlines()

    url_pattern = re.compile(r'(https?://[^\s)]+)')
    urls_to_process = []

    # Collect all URLs and their respective line indices
    for i, line in enumerate(lines):
        url_match = url_pattern.search(line)
        if url_match:
            url = url_match.group(0)
            log_message(f"URL found: {url}")

            # Check if the next line contains 'summarized_content', indicating that the URL has been processed before
            if i + 1 < len(lines) and 'summarized_content' in lines[i + 1].lower():
                log_message("PDF already processed, skipping...")
                continue

            urls_to_process.append(url)

    # Process each URL
    for url in urls_to_process:
        pdf_name = url.split('/')[-1].split('?')[0]
        pdf_dir = os.path.join(os.path.dirname(md_path), 'pdf')
        pdf_path = os.path.join(pdf_dir, f'{pdf_name}.pdf')
        open_chrome_with_profile()
        asyncio.get_event_loop().run_until_complete(download_pdf(url, pdf_name, pdf_dir, pdf_path))
        summarize_pdf_and_update_md(pdf_path, md_path, url)

    log_message(f"Finished processing: {md_path}")

def process_all_markdown_in_directory(directory):
    """Process all markdown files in the specified directory."""
    log_message(f"Processing markdown files in directory: {directory}")

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md') and file != 'index.md':
                md_path = os.path.join(root, file)
                log_message(f"Processing file: {md_path}")
                process_markdown(md_path)

# Example usage
docs_directory = 'docs/System Design/'  # Set your directory path
process_all_markdown_in_directory(docs_directory)
