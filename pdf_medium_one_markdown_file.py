import os
import re
import asyncio
import subprocess
from pyppeteer import connect
import requests
import time

# Path to the sample PDF markdown content
SAMPLE_PDF_MD_PATH = 'samplefiles/pdf.md'

async def download_pdf(url, pdf_name):
    """Download the PDF from the URL and store it in the pdf directory."""
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

    # Scroll to the bottom of the page to load all lazy-loaded content
    await auto_scroll(page)

    # Generate the PDF in the 'pdf/' directory
    if not os.path.exists('pdf'):
        os.makedirs('pdf')
    
    pdf_path = f'pdf/{pdf_name}.pdf'
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
    """Process the markdown file, download PDFs, and update the file with the correct information."""
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
            
            # Check if the next line contains "pdf"
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip().lower()
                print(f"Next line: {next_line}")
                
                if "pdf" in next_line:
                    print(f"Skipping PDF generation because next line contains 'pdf': {next_line}")
                else:
                    # Generate PDF name from URL
                    pdf_name = url.split('/')[-1].split('.')[0]
                    
                    # Step 1: Open Chrome with the profile and remote debugging port
                    open_chrome_with_profile()
                    
                    # Step 2: Add PDF download to the event loop
                    asyncio.get_event_loop().run_until_complete(download_pdf(url, pdf_name))
                    
                    # Step 3: Read sample pdf.md content
                    with open(SAMPLE_PDF_MD_PATH, 'r') as sample_file:
                        pdf_content = sample_file.read().replace("Name.pdf", f"{pdf_name}.pdf")
                    
                    # Step 4: Add the generated content to the markdown file
                    modified_lines.append(pdf_content + '\n')

                    # Wait for 2 seconds before proceeding to the next URL
                    time.sleep(2)

        i += 1

    # Write the modified content back to the markdown file
    with open(md_path, 'w') as file:
        file.writelines(modified_lines)

# Example usage
markdown_file_path = 'example.md'  # Replace with the path to your markdown file
process_markdown(markdown_file_path)
