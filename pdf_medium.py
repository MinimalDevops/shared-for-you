import asyncio
from pyppeteer import connect
import requests

async def main():
    # Get the WebSocket Debugger URL
    response = requests.get("http://localhost:9222/json/version")
    ws_url = response.json()["webSocketDebuggerUrl"]

    # Connect to the running Chrome instance
    browser = await connect(browserWSEndpoint=ws_url)

    # Open a new tab and navigate to the target page
    page = await browser.newPage()
    await page.goto('https://medium.com/geekculture/transactional-data-lakes-a-comparison-of-apache-iceberg-apache-hudi-and-delta-lake-9d7e58fd229b')

    # Scroll to the bottom of the page to load all lazy-loaded content
    await auto_scroll(page)


    # Wait for the page content to load and generate the PDF
    await page.waitForSelector('article')
    await page.pdf({'path': 'result.pdf', 'format': 'A4', 'printBackground': True})

    print("PDF generated successfully!")
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

asyncio.get_event_loop().run_until_complete(main())
