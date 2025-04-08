from pydantic import Field
from typing import Literal, Optional, List, Union
from atomic_agents.schemas.base_schema import BaseIOSchema
import uuid

from .config import AgentConfig

# --- Agent Input Schema ---
class AgentInputSchema(BaseIOSchema):
    """Input schema for the Language Learning Exercise Agent."""
    topic: str = Field(..., description=f"The central theme or subject for the learning exercise (e.g., '{AgentConfig.target_language} greetings', 'ordering food in {AgentConfig.target_language}').")
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="The desired difficulty level for the exercise.")
    target_language: str = Field(default=AgentConfig.target_language, description="The language the user wants to learn.")

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


# --- Union Schema for Agent's Flexible Output ---
# This tells the agent it can output *either* a request for user interaction *or* the final result.
AgentOutputSchema = Union[UserInteractionSchema, EvaluationSchema, FinalOutputSchema]

