from pydantic import Field
from typing import Literal, Optional, List, Union
from atomic_agents.agents.base_agent import BaseIOSchema

from language_agent.tools.image_generator import ImageGeneratorToolInputSchema

from .config import AgentConfig


class AgentInputSchema(BaseIOSchema):
    """Input schema for the Language Learning Exercise Agent."""
    topic: str = Field(..., description=f"The central theme or subject for the learning exercise (e.g., '{AgentConfig.target_language} greetings', 'ordering food in {AgentConfig.target_language}'). If input is empty then use the initially provided topic.")
    target_language: str = Field(default=AgentConfig.target_language, description="The language the user wants to learn.")
    user_input: Optional[str] = Field(None, description="Input from the user based on the exercise. This is the user's response to the exercise.")


class QuizOptionSchema(BaseIOSchema):
    """Schema representing a quiz option."""
    option: str = Field(..., description="The option for the quiz question.")
    is_correct: bool = Field(..., description="Whether the option is the correct answer.")
    feedback: str = Field(..., description="Feedback for the user if the option is correct or incorrect.")


class QuizSchema(BaseIOSchema):
    """Schema representing a quiz question and answer and possible options."""
    question: str = Field(..., description="The question of the quiz.")
    options: Optional[List[QuizOptionSchema]] = Field(None, description="Optional list of answer options for the quiz question.")


class AgentOutputSchema(BaseIOSchema):
    """
    Agent output schema which is sent to the user.
    It can contain multiple things based on the exercise that is generated.
    """
    exercise_type: str = Field(..., description="A descriptive name for the type of exercise generated (e.g., 'Translation Task', 'Listening Comprehension Quiz', 'Image Description').")
    difficulty: Literal["easy", "medium", "hard"]
    response_to_user: str = Field(..., description="The instruction, question or feedback presented to the user.")
    response_to_user_en: str = Field(..., description="The instruction, question or feedback presented to the user in English.")
    # Include the original request for context
    original_topic: str = Field(..., description="The original topic provided by the user.")


class EasyExerciseAgentOutputSchema(AgentOutputSchema):
    """
    Output schema for easy difficulty level. Assumes a text based exercise only.
    """
    difficulty: Literal["easy"]
    text_content: Optional[str] = Field(None, description="Text content for the exercise.")


class MediumExerciseAgentOutputSchema(AgentOutputSchema):
    """
    Output schema for medium difficulty level. Assumes an image based exercise.
    """
    difficulty: Literal["medium"]
    image_generator_tool_input: Optional[ImageGeneratorToolInputSchema] = Field(None, description="Input to the ImageGeneratorTool. A short description describing how to generate the image. The image should be generated once at the beginning only.")


class HardExerciseAgentOutputSchema(AgentOutputSchema):
    """
    Output schema for hard difficulty level. Assumes a quiz based exercise based on an Audio snippet.
    """
    difficulty: Literal["hard"]
    quiz_questions: Optional[List[QuizSchema]] = Field(None, description="List of quiz questions, if the exercise is a quiz.")

# TODO: Add validation using pydantic validators
class UIOutputSchema(AgentOutputSchema):
    """
    Output schema for the user interface.
    """
    text_content: Optional[str] = Field(None, description="Text content for the exercise.")
    image_s3: Optional[str] = Field(None, description="S3 URL of the generated image.")
    audio_s3: Optional[str] = Field(None, description="S3 URL of the generated audio.")
