from typing import List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from pydantic import Field

from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class ExtractVocabularyToolInputSchema(BaseIOSchema):
    """
    Schema for input to a tool for extracting vocabulary (unique alphabetical words) from text.
    Returns a sorted list of unique words found in the text.
    """

    text: str = Field(..., description="The text to extract vocabulary from.")


####################
# OUTPUT SCHEMA(S) #
####################
class ExtractVocabularyToolOutputSchema(BaseIOSchema):
    """This schema represents the output of the Extract Vocabulary tool."""

    vocabulary: List[str] = Field(..., description="The sorted list of unique alphabetical words extracted from the text")
    word_count: int = Field(..., description="The total number of unique words found")


##############
# TOOL LOGIC #
##############
class ExtractVocabularyToolConfig(BaseToolConfig):
    """Configuration for the Extract Vocabulary Tool."""
    
    # No additional configuration needed for this tool


class ExtractVocabularyTool(BaseTool):
    """
    Tool for extracting vocabulary (unique alphabetical words) from text.

    Attributes:
        input_schema (ExtractVocabularyToolInputSchema): The schema for the input data.
        output_schema (ExtractVocabularyToolOutputSchema): The schema for the output data.
    """

    input_schema = ExtractVocabularyToolInputSchema
    output_schema = ExtractVocabularyToolOutputSchema

    def __init__(self, config: ExtractVocabularyToolConfig = ExtractVocabularyToolConfig()):
        """
        Initializes the ExtractVocabularyTool.

        Args:
            config (ExtractVocabularyToolConfig):
                Configuration for the tool, including optional title and description overrides.
        """
        super().__init__(config)

    def extract_vocabulary(self, text: str) -> list:
        """
        Extracts unique alphabetical words from text and sorts them.

        Args:
            text (str): The text to extract vocabulary from.

        Returns:
            list: A sorted list of unique alphabetical words.
        """
        words = set(text.lower().split())
        vocabulary = [word for word in words if word.isalpha()]
        return sorted(vocabulary)

    async def run_async(self, params: ExtractVocabularyToolInputSchema) -> ExtractVocabularyToolOutputSchema:
        """
        Runs the ExtractVocabularyTool asynchronously with the given parameters.

        Args:
            params (ExtractVocabularyToolInputSchema): The input parameters for the tool, adhering to the input schema.

        Returns:
            ExtractVocabularyToolOutputSchema: The output of the tool, adhering to the output schema.
        """
        text = params.text

        # Run the synchronous extract_vocabulary method in a thread pool
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            vocabulary = await loop.run_in_executor(executor, self.extract_vocabulary, text)

        return ExtractVocabularyToolOutputSchema(
            vocabulary=vocabulary,
            word_count=len(vocabulary)
        )

    def run(self, params: ExtractVocabularyToolInputSchema) -> ExtractVocabularyToolOutputSchema:
        """
        Runs the ExtractVocabularyTool synchronously with the given parameters.

        This method creates an event loop in a separate thread to run the asynchronous operations.

        Args:
            params (ExtractVocabularyToolInputSchema): The input parameters for the tool, adhering to the input schema.

        Returns:
            ExtractVocabularyToolOutputSchema: The output of the tool, adhering to the output schema.
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
    tool = ExtractVocabularyTool()
    sample_text = "This is a sample text. It contains some words that will be extracted. This is just a test!"
    result = tool.run(ExtractVocabularyToolInputSchema(text=sample_text))
    print(f"Found {result.word_count} unique words:")
    print(result.vocabulary)