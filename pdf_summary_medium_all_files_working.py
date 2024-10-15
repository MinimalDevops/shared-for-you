import os
import re
import asyncio
import subprocess
import requests
import time
from pyppeteer import connect  # Import connect function

# Path to the sample PDF markdown content
SAMPLE_PDF_MD_PATH = 'samplefiles/pdf.md'

# Parameterize the base URL for summarizing
base_url = "http://172.16.1.10:8001"

async def download_pdf(url, pdf_name, pdf_dir, modified_lines, url_line_index):
    """Download the PDF from the URL and store it in the pdf directory relative to the markdown file."""
    print(f"Attempting to download PDF for URL: {url}")

    # Construct the full path for the PDF
    pdf_path = os.path.join(pdf_dir, f'{pdf_name}.pdf')

    # Initialize the browser connection at the beginning
    response = requests.get("http://localhost:9222/json/version")
    if response.status_code == 200:
        print("Connected to Chrome successfully")
    else:
        print(f"Failed to connect to Chrome: {response.status_code}")
        return

    ws_url = response.json()["webSocketDebuggerUrl"]
    print(f"WebSocket URL: {ws_url}")

    # Initialize browser connection
    browser = await connect(browserWSEndpoint=ws_url)
    browser_connected = True  # Flag to track if the browser is still connected

    try:
        # Check if the PDF already exists
        if os.path.exists(pdf_path):
            print(f"PDF already exists at {pdf_path}, skipping download.")
            # Ensure the browser is closed before summarizing
            await browser.close()
            browser_connected = False
            print("Browser closed as PDF already exists.")
            summarize_pdf_and_update_md(pdf_path, modified_lines, url_line_index)
            return

        # Proceed to download the PDF since it doesn't exist
        page = await browser.newPage()
        await page.goto(url)

        # Handle cookie consent popup if present
        try:
            print("Checking for cookie consent popup...")
            for _ in range(3):
                try:
                    await page.waitForSelector('button[aria-label="Accept all cookies"]', timeout=10000)
                    await page.click('button[aria-label="Accept all cookies"]')
                    print("Accepted cookies.")
                    break
                except Exception as e:
                    print(f"Retrying to accept cookies: {e}")
                    time.sleep(2)
        except Exception as e:
            print(f"Error handling cookie consent: {e}")

        # Scroll the page to trigger lazy-loaded content
        await auto_scroll(page)

        # Ensure the PDF directory exists
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)

        # Generate the PDF and save it
        await page.pdf({'path': pdf_path, 'format': 'A4', 'printBackground': True})
        print(f"PDF generated at {pdf_path}")

    finally:
        # Ensure the browser is closed, even if an exception occurs or PDF already exists
        if browser_connected:
            try:
                print("Closing browser...")
                await browser.close()
            except Exception as e:
                print(f"Error while closing browser: {e}")

    # Continue with summarization and markdown update
    summarize_pdf_and_update_md(pdf_path, modified_lines, url_line_index)

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
    print("Opening Chrome with profile...")
    subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 
                      '--remote-debugging-port=9222', '--profile-directory=Profile 2'])
    time.sleep(2)

def summarize_pdf_and_update_md(pdf_path, modified_lines, url_line_index):
    """Summarize the PDF and update the markdown file, then delete the ingested PDF document."""
    print(f"Starting summarization for {pdf_path}")

    # Step 1: Ingest the PDF
    ingest_url = f"{base_url}/v1/ingest/file"
    with open(pdf_path, 'rb') as file:
        ingest_response = requests.post(ingest_url, files={'file': file})

    if ingest_response.status_code == 200:
        print(f"PDF {pdf_path} ingested successfully.")
    else:
        print(f"Failed to ingest PDF: {ingest_response.status_code}")
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

    print("Sending summarization request...")
    response = requests.post(summarize_url, headers=headers, json=payload)
    summary = response.json().get("summary", "No summary found")
    print(f"Summary: {summary}")

    # Step 3: Generate PDF and summary content
    with open(SAMPLE_PDF_MD_PATH, 'r') as sample_file:
        pdf_content = sample_file.read().replace("Name.pdf", f"{os.path.basename(pdf_path)}")
        pdf_content = pdf_content.replace("summary", summary)

    # Add the content directly after the URL line in the in-memory lines
    modified_lines.insert(url_line_index + 1, pdf_content + '\n')

    print(f"Content updated successfully for line index: {url_line_index}")

    # Step 4: Delete the ingested document
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
            print(f"Document IDs for deletion: {doc_ids_to_delete}")
        else:
            print(f"No Document IDs found for {pdf_name}.")
            return

        for doc_id in doc_ids_to_delete:
            delete_url = f"{base_url}/v1/ingest/{doc_id}"
            delete_response = requests.delete(delete_url)

            if delete_response.status_code == 200:
                print(f"Document with doc_id {doc_id} successfully deleted.")
            else:
                print(f"Failed to delete document with doc_id {doc_id}: {delete_response.status_code}")
    else:
        print(f"Failed to fetch document list: {list_response.status_code}")

def process_markdown(md_path):
    """Process a markdown file and download PDFs."""
    print(f"Processing markdown file: {md_path}")

    with open(md_path, 'r') as file:
        lines = file.readlines()

    url_pattern = re.compile(r'(https?://[^\s)]+)')
    urls_to_process = []

    # Collect all URLs and their respective line indices
    for i, line in enumerate(lines):
        url_match = url_pattern.search(line)
        if url_match:
            url = url_match.group(0)
            print(f"URL found: {url}")

            # Check if the next line contains 'summarized_content', indicating that the URL has been processed before
            if i + 1 < len(lines) and 'summarized_content' in lines[i + 1].lower():
                print("PDF already processed, skipping...")
                continue

            urls_to_process.append((i, url))

    # Create a copy of lines to modify in-memory
    modified_lines = lines[:]

    # Process each URL and update the markdown content in-memory
    for url_line_index, url in urls_to_process:
        pdf_name = url.split('/')[-1].split('?')[0]
        pdf_dir = os.path.join(os.path.dirname(md_path), 'pdf')
        open_chrome_with_profile()
        asyncio.get_event_loop().run_until_complete(download_pdf(url, pdf_name, pdf_dir, modified_lines, url_line_index))

    # Write the updated content back to the markdown file after processing all URLs
    with open(md_path, 'w') as file:
        file.writelines(modified_lines)

    print(f"Finished processing: {md_path}")

def process_all_markdown_in_directory(directory):
    """Process all markdown files in the specified directory."""
    print(f"Processing markdown files in directory: {directory}")

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md') and file != 'index.md':
                md_path = os.path.join(root, file)
                print(f"Processing file: {md_path}")
                process_markdown(md_path)

# Example usage
docs_directory = 'docs/System Design/'  # Set your directory path
process_all_markdown_in_directory(docs_directory)
