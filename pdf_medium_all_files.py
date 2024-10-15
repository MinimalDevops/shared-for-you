import os
import re
import asyncio
import subprocess
from pyppeteer import connect
import requests
import time

# Path to the sample PDF markdown content
SAMPLE_PDF_MD_PATH = 'samplefiles/pdf.md'

async def download_pdf(url, pdf_name, pdf_dir):
    """Download the PDF from the URL and store it in the pdf directory relative to the markdown file."""
    print(f"Attempting to download PDF for URL: {url}")
    
    # Get the WebSocket Debugger URL after launching Chrome
    response = requests.get("http://localhost:9222/json/version")
    if response.status_code == 200:
        print("Connected to Chrome successfully")
    else:
        print(f"Failed to connect to Chrome: {response.status_code}")
    
    ws_url = response.json()["webSocketDebuggerUrl"]
    print(f"WebSocket URL: {ws_url}")

    # Connect to the running Chrome instance
    browser = await connect(browserWSEndpoint=ws_url)

    # Open a new tab and navigate to the target page
    page = await browser.newPage()
    await page.goto(url)

    # Detect and accept cookies if the popup appears, with retry
    try:
        print("Checking for cookie consent popup...")
        retries = 3
        for _ in range(retries):
            try:
                # Wait up to 10 seconds for the consent button to appear
                await page.waitForSelector('button[aria-label="Accept all cookies"]', timeout=10000)
                await page.click('button[aria-label="Accept all cookies"]')
                print("Accepted cookies.")
                break
            except Exception as e:
                print(f"Retrying to accept cookies, attempt failed: {e}")
                time.sleep(2)  # Wait 2 seconds before retrying
        else:
            print("No cookie consent popup found or interaction failed.")
    except Exception as e:
        print("Error while handling cookie consent:", e)

    # Scroll to the bottom of the page to load all lazy-loaded content
    await auto_scroll(page)

    # Ensure the directory exists
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    
    pdf_path = os.path.join(pdf_dir, f'{pdf_name}.pdf')
    await page.pdf({'path': pdf_path, 'format': 'A4', 'printBackground': True})

    print(f"PDF generated successfully at {pdf_path}!")
    await browser.close()

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

                    if(totalHeight >= scrollHeight){
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    ''')

def open_chrome_with_profile():
    """Open Google Chrome with a specific profile and remote debugging port."""
    print("Opening Chrome with profile...")
    subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--remote-debugging-port=9222', '--profile-directory=Profile 2'])
    time.sleep(2)  # Wait for Chrome to open

def process_markdown(md_path):
    """Process a single markdown file, download PDFs, and update the file with the correct information."""
    with open(md_path, 'r') as file:
        lines = file.readlines()
    
    # Adjusted regex to exclude closing brackets from the URL
    url_pattern = re.compile(r'(https?://[^\s)]+)')  
    modified_lines = []
    pdf_downloads = []

    i = 0
    while i < len(lines):
        line = lines[i]
        modified_lines.append(line)
        
        # Search for URL in the current line
        url_match = url_pattern.search(line)
        if url_match:
            url = url_match.group(0)
            print(f"URL found: {url}")
            
            # Check if the next line exists and contains "pdf"
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip().lower()
                print(f"Next line: {next_line}")
                
                if "pdf" in next_line:
                    print(f"Skipping PDF generation because next line contains 'pdf': {next_line}")
                else:
                    # Generate PDF name from URL
                    pdf_name = url.split('/')[-1].split('.')[0]
                    
                    # Determine the path for the pdf directory relative to the markdown file
                    pdf_dir = os.path.join(os.path.dirname(md_path), 'pdf')

                    # Step 1: Open Chrome with the profile and remote debugging port
                    open_chrome_with_profile()
                    
                    # Step 2: Add PDF download to the event loop
                    asyncio.get_event_loop().run_until_complete(download_pdf(url, pdf_name, pdf_dir))
                    
                    # Step 3: Read sample pdf.md content
                    with open(SAMPLE_PDF_MD_PATH, 'r') as sample_file:
                        pdf_content = sample_file.read().replace("Name.pdf", f"{pdf_name}.pdf")
                    
                    # Step 4: Add the generated content to the markdown file
                    modified_lines.append(pdf_content + '\n')

                    # Wait for 2 seconds before proceeding to the next URL
                    time.sleep(2)

            else:
                # Handle case when URL is on the last line
                print(f"URL found on the last line, generating PDF and adding content...")
                pdf_name = url.split('/')[-1].split('.')[0]
                pdf_dir = os.path.join(os.path.dirname(md_path), 'pdf')

                # Open Chrome with profile and download the PDF
                open_chrome_with_profile()
                asyncio.get_event_loop().run_until_complete(download_pdf(url, pdf_name, pdf_dir))

                # Read sample pdf.md content and add to the end
                with open(SAMPLE_PDF_MD_PATH, 'r') as sample_file:
                    pdf_content = sample_file.read().replace("Name.pdf", f"{pdf_name}.pdf")
                
                modified_lines.append(pdf_content + '\n')
                time.sleep(2)

        i += 1

    # Write the modified content back to the markdown file
    with open(md_path, 'w') as file:
        file.writelines(modified_lines)

def process_all_markdown_in_directory(directory):
    """Recursively process all markdown files in the directory, ignoring index.md."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md') and file != 'index.md':
                markdown_path = os.path.join(root, file)
                print(f"Processing file: {markdown_path}")
                process_markdown(markdown_path)
                print(f"Finished processing: {markdown_path}")

# Example usage
docs_directory = 'docs/System Design/'  # Replace with the root directory where your markdown files are stored
process_all_markdown_in_directory(docs_directory)
