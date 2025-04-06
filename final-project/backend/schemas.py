from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Union
from atomic_agents.schemas.base_schema import BaseIOSchema
import uuid

# --- Agent Input Schema ---
class AgentInputSchema(BaseIOSchema):
    """Input schema for the Language Learning Exercise Agent."""
    topic: str = Field(..., description="The central theme or subject for the learning exercise (e.g., 'Italian greetings', 'ordering food in French').")
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="The desired difficulty level for the exercise.")
    target_language: str = Field(default="Italian", description="The language the user wants to learn.")
    user_context: Optional[str] = Field(None, description="Optional context about the user or their learning goals (e.g., 'beginner student', 'traveling next month').")

# --- Agent Intermediate & Tool Output Schemas (used within the agent flow) ---
class ContentGenerationSchema(BaseIOSchema):
    """Schema representing generated content like stories or dialogues."""
    content_type: Literal["story", "dialogue", "transcript_summary"] = Field(..., description="Type of content generated.")
    text: str = Field(..., description="The generated text content.")
    topic: str = Field(..., description="The topic the content relates to.")
    target_language: str = Field(..., description="The language of the content.")

class MediaSchema(BaseIOSchema):
    """Schema representing generated media (image or audio)."""
    media_type: Literal["image", "audio"] = Field(..., description="Type of media generated.")
    s3_path: str = Field(..., description="The S3 path where the media is stored.")
    source_text_or_prompt: str = Field(..., description="The text or prompt used to generate the media.")

class QuizSchema(BaseIOSchema):
    """Schema representing a generated quiz question and its answer."""
    question: str = Field(..., description="The quiz question.")
    correct_answer: str = Field(..., description="The correct answer to the question.")
    # We might add question_type later (e.g., multiple-choice, translation)

class TranslationRequestSchema(BaseIOSchema):
    """Schema for requesting a translation."""
    text_to_translate: str = Field(..., description="The text needing translation.")
    source_language: str = Field(..., description="The original language of the text.")
    target_language: str = Field(..., description="The language to translate into.")

class TranslationResponseSchema(BaseIOSchema):
    """Schema for the result of a translation."""
    original_text: str = Field(..., description="The original text provided.")
    translated_text: str = Field(..., description="The translated text.")
    source_language: str = Field(..., description="The original language.")
    target_language: str = Field(..., description="The target language.")

class UserInteractionSchema(BaseIOSchema):
    """Schema representing an interaction point requiring user input."""
    interaction_type: Literal["ask_for_translation", "ask_for_description", "present_quiz"] = Field(..., description="The type of interaction requested.")
    prompt_to_user: str = Field(..., description="The instruction or question presented to the user.")
    media_s3_path: Optional[str] = Field(None, description="Optional S3 path for associated media (image/audio) for the interaction.")
    # We might need a way to store context for evaluating the user's response later
    interaction_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique ID for this interaction instance.")

class EvaluationSchema(BaseIOSchema):
    """Schema representing the evaluation of a user's response."""
    evaluation_feedback: str = Field(..., description="Feedback provided to the user about their response.")
    is_correct: Optional[bool] = Field(None, description="Whether the user's response was deemed correct (if applicable).")
    interaction_id: uuid.UUID = Field(..., description="The ID of the interaction being evaluated.")

# --- Agent Final Output Schema ---
class FinalOutputSchema(BaseIOSchema):
    """Final output schema when the exercise generation is complete."""
    exercise_type: str = Field(..., description="A descriptive name for the type of exercise generated (e.g., 'Translation Task', 'Listening Comprehension Quiz', 'Image Description').")
    difficulty: Literal["easy", "medium", "hard"]
    text_content: Optional[str] = Field(None, description="Main text content of the exercise, if any.")
    image_s3_path: Optional[str] = Field(None, description="S3 path to an associated image, if any.")
    audio_s3_path: Optional[str] = Field(None, description="S3 path to associated audio, if any.")
    quiz_questions: Optional[List[QuizSchema]] = Field(None, description="List of quiz questions, if the exercise is a quiz.")
    # Include the original request for context
    original_topic: str
    original_target_language: str

# --- Agent Memory/State Schema ---
class AgentStateSchema(BaseIOSchema):
    """Schema to hold the agent's state between steps or turns."""
    current_step: str = Field(..., description="Identifier for the current stage of the exercise generation process.")
    original_input: AgentInputSchema
    generated_story_id: Optional[uuid.UUID] = None
    generated_story_text: Optional[str] = None
    generated_image_s3_path: Optional[str] = None
    generated_audio_s3_path: Optional[str] = None
    generated_quiz_ids: List[uuid.UUID] = Field(default_factory=list)
    # Store intermediate results if needed for multi-step processes
    intermediate_data: Optional[Dict[str, Any]] = None
    last_interaction_id: Optional[uuid.UUID] = None # Track the ID needed for evaluation


# --- Union Schema for Agent's Flexible Output ---
# This tells the agent it can output *either* a request for user interaction *or* the final result.
AgentOutputSchema = Union[UserInteractionSchema, EvaluationSchema, FinalOutputSchema]

