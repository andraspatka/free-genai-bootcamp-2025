from .schemas import WebScraperInputSchema, WebScraperOutputSchema
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def run_web_scraper(input_data: WebScraperInputSchema) -> WebScraperOutputSchema:
    """Scrapes text content from a given URL."""
    logger.info(f"Scraping URL: {input_data.url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(input_data.url, headers=headers, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text, strip leading/trailing whitespace, separate lines
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text_content = '\n'.join(chunk for chunk in chunks if chunk)

        logger.info(f"Successfully scraped {len(text_content)} characters from {input_data.url}")
        return WebScraperOutputSchema(url=input_data.url, text_content=text_content)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping URL {input_data.url}: {e}", exc_info=True)
        # Return empty content or re-raise
        return WebScraperOutputSchema(url=input_data.url, text_content="")
    except Exception as e:
        logger.error(f"Unexpected error scraping {input_data.url}: {e}", exc_info=True)
        return WebScraperOutputSchema(url=input_data.url, text_content="")

# Example usage (for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Replace with a real URL for testing
    test_input = WebScraperInputSchema(url="https://www.example.com")
    output = run_web_scraper(test_input)
    print(output.model_dump_json(indent=2))

