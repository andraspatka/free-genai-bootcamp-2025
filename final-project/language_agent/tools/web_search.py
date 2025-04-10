from duckduckgo_search import DDGS

import os
from typing import List, Literal, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

import aiohttp
from pydantic import Field

from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class DuckDuckGoSearchToolInputSchema(BaseIOSchema):
    """
    Schema for input to a tool for searching for information, news, references, and other content using DuckDuckGo.
    Returns a list of search results with a short description or content snippet and URLs for further exploration
    """

    queries: List[str] = Field(..., description="List of search queries.")
    category: Optional[Literal["general", "news", "social_media"]] = Field(
        "general", description="Category of the search queries."
    )


####################
# OUTPUT SCHEMA(S) #
####################
class DuckDuckGoSearchResultItemSchema(BaseIOSchema):
    """This schema represents a single search result item"""

    href: str = Field(..., description="The URL of the search result")
    title: str = Field(..., description="The title of the search result")
    body: Optional[str] = Field(None, description="The content snippet of the search result")


class DuckDuckGoSearchToolOutputSchema(BaseIOSchema):
    """This schema represents the output of the DuckDuckGo search tool."""

    results: List[DuckDuckGoSearchResultItemSchema] = Field(..., description="List of search result items")
    category: Optional[str] = Field(None, description="The category of the search results")


##############
# TOOL LOGIC #
##############
class DuckDuckGoSearchToolConfig(BaseToolConfig):
    max_results: int = 10


class DuckDuckGoSearchTool(BaseTool):
    """
    Tool for performing searches on DuckDuckGo based on the provided queries and category.

    Attributes:
        input_schema (DuckDuckGoSearchToolInputSchema): The schema for the input data.
        output_schema (DuckDuckGoSearchToolOutputSchema): The schema for the output data.
        max_results (int): The maximum number of search results to return.
    """

    input_schema = DuckDuckGoSearchToolInputSchema
    output_schema = DuckDuckGoSearchToolOutputSchema

    def __init__(self, config: DuckDuckGoSearchToolConfig = DuckDuckGoSearchToolConfig()):
        """
        Initializes the DuckDuckGoTool.

        Args:
            config (DuckDuckGoDuckDuckGoSearchToolConfigSearchToolConfig):
                Configuration for the tool, including base URL, max results, and optional title and description overrides.
        """
        super().__init__(config)
        self.max_results = config.max_results

    async def _fetch_search_results(self, query: str) -> List[dict]:
        """
        Fetches search results for a single query asynchronously.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            query (str): The search query.

        Returns:
            List[dict]: A list of search result dictionaries.

        Raises:
            Exception: If the request to DuckDuckGo fails.
        """

        results = DDGS().text(query, max_results=self.max_results)
        if results:
            return results


    async def run_async(
        self, params: DuckDuckGoSearchToolInputSchema, max_results: Optional[int] = None
    ) -> DuckDuckGoSearchToolOutputSchema:
        """
        Runs the DuckDuckGoTool asynchronously with the given parameters.

        Args:
            params (DuckDuckGoSearchToolInputSchema): The input parameters for the tool, adhering to the input schema.
            max_results (Optional[int]): The maximum number of search results to return.

        Returns:
            DuckDuckGoSearchToolOutputSchema: The output of the tool, adhering to the output schema.

        Raises:
            ValueError: If the base URL is not provided.
            Exception: If the request to DuckDuckGo fails.
        """
        
        tasks = [self._fetch_search_results(query) for query in params.queries]
        results = await asyncio.gather(*tasks)
        return results

    def run(self, params: DuckDuckGoSearchToolInputSchema, max_results: Optional[int] = None) -> DuckDuckGoSearchToolOutputSchema:
        """
        Runs the DuckDuckGoTool synchronously with the given parameters.

        This method creates an event loop in a separate thread to run the asynchronous operations.

        Args:
            params (DuckDuckGoSearchToolInputSchema): The input parameters for the tool, adhering to the input schema.
            max_results (Optional[int]): The maximum number of search results to return.

        Returns:
            DuckDuckGoSearchToolOutputSchema: The output of the tool, adhering to the output schema.

        Raises:
            ValueError: If the base URL is not provided.
            Exception: If the request to DuckDuckGo fails.
        """
        with ThreadPoolExecutor() as executor:
            return executor.submit(asyncio.run, self.run_async(params, max_results)).result()


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    from rich.console import Console
    rich_console = Console()

    search_tool_instance = DuckDuckGoSearchTool(
        config=DuckDuckGoSearchToolConfig(max_results=5)
    )

    search_input = DuckDuckGoSearchTool.input_schema(
        queries=["Python programming", "Machine learning", "Artificial intelligence"],
    )

    output = search_tool_instance.run(search_input)

    rich_console.print(output)
