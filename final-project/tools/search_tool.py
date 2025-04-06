from .schemas import SearchInputSchema, SearchOutputSchema, SearchResultSchema
from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

def run_search(input_data: SearchInputSchema) -> SearchOutputSchema:
    """Performs a web search using DuckDuckGo."""
    logger.info(f"Performing search for: {input_data.query}")
    try:
        with DDGS() as ddgs:
            # max_results=5 to keep it manageable
            results = list(ddgs.text(input_data.query, max_results=5))

        output_results = [
            SearchResultSchema(
                title=r.get('title', 'N/A'),
                url=r.get('href', ''),
                snippet=r.get('body', '')
            ) for r in results if r.get('href') # Ensure there is a URL
        ]

        logger.info(f"Found {len(output_results)} results.")
        return SearchOutputSchema(results=output_results)
    except Exception as e:
        logger.error(f"Error during DuckDuckGo search: {e}", exc_info=True)
        # Return empty results on error, or raise specific exception
        return SearchOutputSchema(results=[])

# Example usage (for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_input = SearchInputSchema(query="Italian language learning exercises")
    output = run_search(test_input)
    print(output.model_dump_json(indent=2))
