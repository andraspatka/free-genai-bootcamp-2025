from pydantic import Field
from typing import Literal, Optional, List, Union
from atomic_agents.agents.base_agent import BaseIOSchema

from .config import AgentConfig

# --- Agent Input Schema ---
class AgentInputSchema(BaseIOSchema):
    """Input schema for the Language Learning Exercise Agent."""
    topic: str = Field(..., description=f"The central theme or subject for the learning exercise (e.g., '{AgentConfig.target_language} greetings', 'ordering food in {AgentConfig.target_language}'). If input is empty then use the initially provided topic.")
    difficulty: Literal["easy", "medium", "hard", "none"] = Field(..., description="The desired difficulty level for the exercise. Use 'none' if the difficulty was already specified once.")
    target_language: str = Field(default=AgentConfig.target_language, description="The language the user wants to learn.")
    follow_up: Optional[str] = Field(None, description="Any additional instructions or follow-up questions from the user.")

class QuizSchema(BaseIOSchema):
    """Schema representing a quiz question and answer and possible options."""
    question: str = Field(..., description="The question of the quiz.")
    answer: str = Field(..., description="The correct answer to the quiz question.")
    options: Optional[List[str]] = Field(None, description="Optional list of answer options for the quiz question.")

# --- Agent Final Output Schema ---
class AgentOutputSchema(BaseIOSchema):
    """
    Agent output schema which is sent to the user.
    It can contain multiple things based on the exercise that is generated.
    """
    exercise_type: str = Field(..., description="A descriptive name for the type of exercise generated (e.g., 'Translation Task', 'Listening Comprehension Quiz', 'Image Description').")
    difficulty: Literal["easy", "medium", "hard"]
    text_content: Optional[str] = Field(None, description="Main text content of the exercise, if any.")
    response_to_user: str = Field(..., description="The instruction, question or feedback presented to the user.")
    image_s3_path: Optional[str] = Field(None, description="S3 path to an associated image, if any.")
    quiz_questions: Optional[List[QuizSchema]] = Field(None, description="List of quiz questions, if the exercise is a quiz.")
    # Include the original request for context
    original_topic: str
    original_target_language: str
    original_difficulty: Literal["easy", "medium", "hard"]
