from typing import Dict, Type, Callable, Tuple
from pydantic import BaseModel

# Import tool functions and their input schemas
from ..tools import search_tool, web_scraper_tool, youtube_tool, tts_tool, tti_tool, s3_tool, db_tool
from ..tools.schemas import (
    SearchInputSchema, SearchOutputSchema,
    WebScraperInputSchema, WebScraperOutputSchema,
    YouTubeInputSchema, YouTubeOutputSchema,
    TTSInputSchema, TTSOutputSchema,
    TTIInputSchema, TTIOutputSchema,
    S3UploadInputSchema, S3UploadOutputSchema, # S3 upload might be called directly by others
    CreateStoryInputSchema, CreateStoryOutputSchema,
    CreateQuizInputSchema, CreateQuizOutputSchema,
    CreateQuizAnswerInputSchema, CreateQuizAnswerOutputSchema,
    GetStoryInputSchema, GetStoryOutputSchema,
    BaseToolInputSchema
)

# Define the structure for the tool registry
# Maps tool name (str) to a tuple of (function, input_schema)
ToolRegistryType = Dict[str, Tuple[Callable[[BaseModel], BaseModel], Type[BaseModel]]]

TOOL_REGISTRY: ToolRegistryType = {
    "web_search": (search_tool.run_search, SearchInputSchema),
    "scrape_website": (web_scraper_tool.run_web_scraper, WebScraperInputSchema),
    "get_youtube_transcript": (youtube_tool.get_youtube_transcript, YouTubeInputSchema),
    "generate_speech": (tts_tool.generate_speech, TTSInputSchema),
    "generate_image": (tti_tool.generate_image, TTIInputSchema),
    # S3 upload is often used *by* other tools, might not be exposed directly to LLM
    # "upload_to_s3": (s3_tool.upload_to_s3, S3UploadInputSchema), # Decide if agent should call this

    # Database Tools
    "create_story_record": (db_tool.create_story, CreateStoryInputSchema),
    "create_quiz_record": (db_tool.create_quiz, CreateQuizInputSchema),
    "create_quiz_answer_record": (db_tool.create_quiz_answer, CreateQuizAnswerInputSchema),
    "find_stories": (db_tool.get_stories, GetStoryInputSchema),
    # Add other DB operations here as needed (get_quiz, update_story, etc.)
}

def get_tool_function(tool_name: str) -> Callable[[BaseModel], BaseModel] | None:
    """Gets the function associated with a tool name."""
    tool_info = TOOL_REGISTRY.get(tool_name)
    return tool_info[0] if tool_info else None

def get_tool_input_schema(tool_name: str) -> Type[BaseModel] | None:
    """Gets the input schema class associated with a tool name."""
    tool_info = TOOL_REGISTRY.get(tool_name)
    return tool_info[1] if tool_info else None

def list_available_tools() -> Dict[str, str]:
    """Returns a dictionary of available tool names and their descriptions (from input schema)."""
    tool_descriptions = {}
    for name, (_, schema) in TOOL_REGISTRY.items():
        tool_descriptions[name] = schema.__doc__ or "No description available."
    return tool_descriptions

