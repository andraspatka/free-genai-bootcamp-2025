from pydantic import Field
from typing import Literal, Optional, List, Union
from atomic_agents.agents.base_agent import BaseIOSchema

from language_agent.tools.image_generator import ImageGeneratorToolInputSchema

from .config import AgentConfig

class AgentInputSchema(BaseIOSchema):
    """Input schema for the Language Learning Exercise Agent."""
    topic: str = Field(..., description=f"The central theme or subject for the learning exercise (e.g., '{AgentConfig.target_language} greetings', 'ordering food in {AgentConfig.target_language}'). If input is empty then use the initially provided topic.")
    target_language: str = Field(default=AgentConfig.target_language, description="The language the user wants to learn.")
    follow_up: Optional[str] = Field(None, description="Any additional instructions or follow-up questions from the user.")


class QuizSchema(BaseIOSchema):
    """Schema representing a quiz question and answer and possible options."""
    question: str = Field(..., description="The question of the quiz.")
    options: Optional[List[QuizOptionSchema]] = Field(None, description="Optional list of answer options for the quiz question.")


class QuizOptionSchema(BaseIOSchema):
    """Schema representing a quiz option."""
    option: str = Field(..., description="The option for the quiz question.")
    is_correct: bool = Field(..., description="Whether the option is the correct answer.")
    feedback: str = Field(..., description="Feedback for the user if the option is correct or incorrect.")


class AgentOutputSchema(BaseIOSchema):
    """
    Agent output schema which is sent to the user.
    It can contain multiple things based on the exercise that is generated.
    """
    exercise_type: str = Field(..., description="A descriptive name for the type of exercise generated (e.g., 'Translation Task', 'Listening Comprehension Quiz', 'Image Description').")
    difficulty: Literal["easy", "medium", "hard"]
    text_content: Optional[str] = Field(None, description="Main text content of the exercise, if any.")
    response_to_user: str = Field(..., description="The instruction, question or feedback presented to the user.")
    # Include the original request for context
    original_topic: str
    original_target_language: str
    original_difficulty: Literal["easy", "medium", "hard"]


class EasyExerciseAgentOutputSchema(AgentOutputSchema):
    """
    Output schema for easy difficulty level. Assumes a text based exercise only.
    """
    difficulty: Literal["easy"]


class MediumExerciseAgentOutputSchema(AgentOutputSchema):
    """
    Output schema for medium difficulty level. Assumes an image based exercise.
    """
    difficulty: Literal["medium"]
    image_generator_tool_input: ImageGeneratorToolInputSchema = Field(..., description="Input to the ImageGeneratorTool. A short description describing how to generate the image")


class HardExerciseAgentOutputSchema(AgentOutputSchema):
    """
    Output schema for hard difficulty level. Assumes a quiz based exercise based on an Audio snippet.
    """
    difficulty: Literal["hard"]
    quiz_questions: Optional[List[QuizSchema]] = Field(None, description="List of quiz questions, if the exercise is a quiz.")

