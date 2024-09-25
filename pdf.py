import asyncio
from pyppeteer import launch
import logging

logging.basicConfig(level=logging.DEBUG)

async def main():
    # Path to the system-installed Chrome
    chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

    try:
        browser = await launch({
            'headless': False,  # Run in non-headless mode to view interactions
            'userDataDir': '/Users/tapinder.singh/Library/Application Support/Google/Chrome/Profile 2',  # Authenticated profile
            'executablePath': chrome_path,  # System Chrome executable path
            #'args': ['--flag-switches-begin', '--flag-switches-end'],  # Fix permission issues
            'dumpio': True,  # Enable logging
        })

        page = await browser.newPage()

        # Navigate to the Medium article
        logging.info("Navigating to the target webpage...")
        await page.goto('https://medium.com/geekculture/transactional-data-lakes-a-comparison-of-apache-iceberg-apache-hudi-and-delta-lake-9d7e58fd229b', timeout=60000)

        logging.info("Waiting for page content to load...")

        # Scroll to the bottom to trigger lazy-loading
        await auto_scroll(page)

        # Ensure that the main article content is loaded (waiting for article body)
        await page.waitForSelector('article', timeout=30000)

        # Add a delay to allow dynamic content to fully render (e.g., for comments or late-loading elements)
        await asyncio.sleep(5)  # Wait for 5 seconds to ensure all JS content is loaded

        # Generate the PDF
        logging.info("Generating the PDF...")
        await page.pdf({'path': 'result.pdf', 'format': 'A4', 'printBackground': True})

        logging.info("PDF generated successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if 'browser' in locals():
            await browser.close()
            logging.info("Browser closed.")

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

# Add retry logic to retry up to 3 times if there's a failure
async def run_with_retries():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await main()
            break  # Exit loop if successful
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt + 1 == max_retries:
                logging.error("Max retries reached. Exiting.")
                raise

asyncio.get_event_loop().run_until_complete(run_with_retries())
