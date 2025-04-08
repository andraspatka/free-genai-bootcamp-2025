import requests
from html2text import HTML2Text
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from pydantic import Field

from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class PageContentGetterToolInputSchema(BaseIOSchema):
    """
    Schema for input to a tool for retrieving and converting HTML content from a URL into markdown text.
    Returns the content of the page in a readable markdown format.
    """

    url: str = Field(..., description="The URL of the webpage to retrieve content from.")


####################
# OUTPUT SCHEMA(S) #
####################
class PageContentGetterToolOutputSchema(BaseIOSchema):
    """This schema represents the output of the Page Content Getter tool."""

    content: str = Field(..., description="The markdown content extracted from the webpage")
    url: str = Field(..., description="The URL of the webpage that was processed")


##############
# TOOL LOGIC #
##############
class PageContentGetterToolConfig(BaseToolConfig):
    """Configuration for the Page Content Getter Tool."""

    max_content_length: int = 4000


class PageContentGetterTool(BaseTool):
    """
    Tool for retrieving HTML content from a URL and converting it to markdown text.

    Attributes:
        input_schema (PageContentGetterToolInputSchema): The schema for the input data.
        output_schema (PageContentGetterToolOutputSchema): The schema for the output data.
        max_content_length (int): The maximum length of content to return.
    """

    input_schema = PageContentGetterToolInputSchema
    output_schema = PageContentGetterToolOutputSchema

    def __init__(self, config: PageContentGetterToolConfig = PageContentGetterToolConfig()):
        """
        Initializes the PageContentGetterTool.

        Args:
            config (PageContentGetterToolConfig):
                Configuration for the tool, including max content length and optional title and description overrides.
        """
        super().__init__(config)
        self.max_content_length = config.max_content_length

    def get_page_content(self, url: str) -> str:
        """
        Fetches HTML content from a URL and converts it to markdown.

        Args:
            url (str): The URL to fetch content from.

        Returns:
            str: The markdown content extracted from the webpage.

        Raises:
            Exception: If the request to the URL fails.
        """
        response = requests.get(url)
        h = HTML2Text()
        h.ignore_links = False
        content = h.handle(response.text)
        return content[:self.max_content_length] if len(content) > self.max_content_length else content

    async def run_async(self, params: PageContentGetterToolInputSchema) -> PageContentGetterToolOutputSchema:
        """
        Runs the PageContentGetterTool asynchronously with the given parameters.

        Args:
            params (PageContentGetterToolInputSchema): The input parameters for the tool, adhering to the input schema.

        Returns:
            PageContentGetterToolOutputSchema: The output of the tool, adhering to the output schema.

        Raises:
            Exception: If the request to the URL fails.
        """
        url = params.url

        # Run the synchronous get_page_content method in a thread pool
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(executor, self.get_page_content, url)

        return PageContentGetterToolOutputSchema(
            content=content,
            url=url
        )

    def run(self, params: PageContentGetterToolInputSchema) -> PageContentGetterToolOutputSchema:
        """
        Runs the PageContentGetterTool synchronously with the given parameters.

        This method creates an event loop in a separate thread to run the asynchronous operations.

        Args:
            params (PageContentGetterToolInputSchema): The input parameters for the tool, adhering to the input schema.

        Returns:
            PageContentGetterToolOutputSchema: The output of the tool, adhering to the output schema.

        Raises:
            Exception: If the request to the URL fails.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run_async(params))
        finally:
            loop.close()


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    # Example usage
    tool = PageContentGetterTool()
    result = tool.run(PageContentGetterToolInputSchema(url="https://example.com"))
    print(f"Content from {result.url}:")
    print(result.content[:200] + "..." if len(result.content) > 200 else result.content)