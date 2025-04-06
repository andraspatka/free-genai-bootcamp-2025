from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid

class BaseToolInputSchema(BaseModel):
    pass # Base class for tool inputs

class BaseToolOutputSchema(BaseModel):
    pass # Base class for tool outputs

# --- Search Tool Schemas ---
class SearchInputSchema(BaseToolInputSchema):
    query: str = Field(..., description="The search query.")

class SearchResultSchema(BaseModel):
    title: str
    url: str
    snippet: str

class SearchOutputSchema(BaseToolOutputSchema):
    results: List[SearchResultSchema] = Field(..., description="List of search results.")

# --- Web Scraper Tool Schemas ---
class WebScraperInputSchema(BaseToolInputSchema):
    url: str = Field(..., description="The URL of the website to scrape.")

class WebScraperOutputSchema(BaseToolOutputSchema):
    url: str = Field(..., description="The URL scraped.")
    text_content: str = Field(..., description="The extracted text content from the website.")

# --- YouTube Tool Schemas ---
class YouTubeInputSchema(BaseToolInputSchema):
    url: str = Field(..., description="The URL of the YouTube video.")

class YouTubeTranscriptChunkSchema(BaseModel):
    text: str
    start: float
    duration: float

class YouTubeOutputSchema(BaseToolOutputSchema):
    video_id: str = Field(..., description="The ID of the YouTube video.")
    title: str = Field(..., description="The title of the YouTube video.")
    transcript: List[YouTubeTranscriptChunkSchema] = Field(..., description="The structured transcript of the video.")

# --- Text-to-Speech (TTS) Tool Schemas ---
class TTSInputSchema(BaseToolInputSchema):
    text_to_speak: str = Field(..., description="The text to convert to speech.")
    output_filename_prefix: str = Field(..., description="A prefix for the output audio filename (e.g., topic_story).")
    s3_path_prefix: str = Field("audio", description="The prefix for the S3 path (e.g., 'audio', 'quiz_audio').")

class TTSOutputSchema(BaseToolOutputSchema):
    s3_path: str = Field(..., description="The path to the generated audio file in the S3 bucket.")
    text_spoken: str = Field(..., description="The original text that was converted to speech.")

# --- Text-to-Image (TTI) Tool Schemas ---
class TTIInputSchema(BaseToolInputSchema):
    prompt: str = Field(..., description="The prompt to generate an image for.")
    output_filename_prefix: str = Field(..., description="A prefix for the output image filename (e.g., topic_visual).")
    s3_path_prefix: str = Field("images", description="The prefix for the S3 path (e.g., 'images', 'story_images').")

class TTIOutputSchema(BaseToolOutputSchema):
    s3_path: str = Field(..., description="The path to the generated image file in the S3 bucket.")
    prompt_used: str = Field(..., description="The prompt used for generation.")

# --- S3 Tool Schemas ---
class S3UploadInputSchema(BaseToolInputSchema):
    file_content: bytes = Field(..., description="The content of the file to upload as bytes.")
    s3_key: str = Field(..., description="The full key (path and filename) for the object in the S3 bucket.")
    content_type: Optional[str] = Field(None, description="The MIME type of the file (e.g., 'audio/mpeg', 'image/png').")

class S3UploadOutputSchema(BaseToolOutputSchema):
    s3_path: str = Field(..., description="The full S3 path (bucket/key) of the uploaded object.")
    url: Optional[str] = Field(None, description="Public URL if the bucket/object permissions allow.") # Optional, might not be public

# --- Database Tool Schemas ---

# Specific schemas for DB operations
class CreateStoryInputSchema(BaseToolInputSchema):
    topic: str = Field(..., description="The topic of the story.")
    story: Optional[str] = Field(None, description="The text content of the story.")
    image_s3_path: Optional[str] = Field(None, description="S3 path for the story image.")
    audio_s3_path: Optional[str] = Field(None, description="S3 path for the story audio.")

class CreateStoryOutputSchema(BaseToolOutputSchema):
    story_id: uuid.UUID = Field(..., description="The UUID of the created story.")
    topic: str

class CreateQuizInputSchema(BaseToolInputSchema):
    story_id: uuid.UUID = Field(..., description="The UUID of the parent story.")
    question: str = Field(..., description="The quiz question.")
    answer: str = Field(..., description="The correct answer to the quiz question.")

class CreateQuizOutputSchema(BaseToolOutputSchema):
    quiz_id: uuid.UUID = Field(..., description="The UUID of the created quiz.")
    story_id: uuid.UUID

class CreateQuizAnswerInputSchema(BaseToolInputSchema):
    quiz_id: uuid.UUID = Field(..., description="The UUID of the parent quiz.")
    user_answer: str = Field(..., description="The answer submitted by the user.")
    is_correct: Optional[bool] = Field(None, description="Whether the user answer is correct (if evaluated).")

class CreateQuizAnswerOutputSchema(BaseToolOutputSchema):
    quiz_answer_id: uuid.UUID = Field(..., description="The UUID of the created quiz answer record.")
    quiz_id: uuid.UUID

class GetStoryInputSchema(BaseToolInputSchema):
    story_id: Optional[uuid.UUID] = Field(None, description="Get by specific ID.")
    topic: Optional[str] = Field(None, description="Get by topic.")

class StorySchema(BaseModel): # For returning data
    id: uuid.UUID
    topic: str
    story: Optional[str]
    image: Optional[str]
    audio: Optional[str]

    class Config:
        orm_mode = True # Allow conversion from SQLAlchemy model

class GetStoryOutputSchema(BaseToolOutputSchema):
    stories: List[StorySchema] = Field(..., description="List of stories found.")

# ... Add schemas for GetQuiz, GetQuizAnswer, Update operations etc. as needed

