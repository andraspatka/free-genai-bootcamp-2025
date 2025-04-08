import os
import logging
from typing import List, Type, Union, Optional

from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.schemas.chat_message import ChatMessage
from atomic_agents.schemas.tool_call import ToolCall, ToolCallResponse
from atomic_agents.systems.agent_system import AgentSystem
from atomic_agents.clients.openai_client import OpenAIClient

from .config import AgentConfig
from .schemas import (
    AgentInputSchema, AgentOutputSchema, FinalOutputSchema,
    UserInteractionSchema
)
from ..tools.schemas import BaseToolInputSchema, BaseToolOutputSchema # For type hinting


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LanguageExerciseAgent(BaseAgent):
    """Agent responsible for generating language learning exercises based on user requests."""

    def __init__(self):
        super().__init__(
            client=instructor.from_openai(openai.OpenAI(api_key=AgentConfig.api_key)),
            model=AgentConfig.model,
            system_prompt_generator=SystemPromptGenerator(
                background=[
                    "You are a language teacher specialized in creating interactive and engaging language learning exercises.",
                    "Your goal is to generate an engaging exercise based on the user's specified topic, difficulty, and target language."
                ]
                steps=[
                    "Analyze the user's request (topic, difficulty, language, context).",
                    "Based on the difficulty, decide on an appropriate exercise type (e.g., translation, listening quiz, image description).",
                    "If necessary, use the available tools to gather information (search, web scrape, YouTube) or generate content (story, image, audio).",
                    "Store generated assets (audio, image) using the S3 tool (implicitly via TTS/TTI tools) and record information (stories, quizzes) in the database using the DB tools.",
                    "Construct the exercise. This might involve:",
                    "    - Asking the user to perform a task (translate text, describe an image).",
                    "    - Presenting a quiz. If a quiz already exists for the given topic, then fetch the quiz details from the database using the DB tools.",
                    "    - Simply providing generated content (story, audio) as the exercise..",
                    "If the exercise requires user input, you will output a `UserInteractionSchema`. The system will handle getting the user's response.",
                    "If you receive user input (as part of the chat history), evaluate it using your language skills. Output the evaluation using `EvaluationSchema`.",
                    "Once the entire exercise flow is complete (content generated, presented, and potentially evaluated), output the final result using `FinalOutputSchema`.",
                ]
                output_instructions=[
                    "Always use the specified target language for the exercise content.",
                    "Adhere strictly to the requested difficulty level.",
                    "Use tools step-by-step. Do not try to chain too many actions in one thought.",
                    "When using tools, provide clear and specific inputs based on the tool's input schema.",
                    "Reference generated content (e.g., story ID, S3 paths) when creating related items (e.g., quizzes for a story).",
                    "If you need to ask the user for input, structure your response using `UserInteractionSchema`.",
                    "If you need to provide feedback on user input, use `EvaluationSchema`.",
                    "When the task is fully complete, use `FinalOutputSchema`.",
                ]
            ),
            input_schema=AgentInputSchema,
            output_schema=AgentOutputSchema,
        )

        logger.info("LanguageExerciseAgent initialized.")


    def clear_memory(self):
        self.memory.history = []
        self.memory.current_turn_id = None



# Example Usage (typically called from the frontend)
if __name__ == '__main__':
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    from rich import box
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    logger.info("Running agent example...")

    # 1. Initialize the agent
    agent = LanguageExerciseAgent()

    # 2. Define the initial request
    initial_request = AgentInputSchema(
        topic="Ordering coffee",
        difficulty="easy",
        target_language="Italian"
    )

    # 3. Run the agent for the first time
    response = agent.run(initial_request)

    print("\n--- Agent Response 1 ---")
    print(response.model_dump_json(indent=2))

    # 4. Simulate conversation flow (if response requires interaction)
    chat_history = agent.agent_system.memory.get_messages() # Get history from the first run

    if isinstance(response, UserInteractionSchema):
        print("\n--- Simulating User Input --- stimulating")
        user_reply_content = "Vorrei un caffè, per favore." # Example user response
        user_message = ChatMessage(role="user", content=user_reply_content)

        # 5. Run the agent again with the user's response
        response_2 = agent.run(user_message, chat_history=chat_history)

        print("\n--- Agent Response 2 (Evaluation/Next Step) ---")
        print(response_2.model_dump_json(indent=2))

        # Continue the loop as needed...

    elif isinstance(response, FinalOutputSchema):
        print("\n--- Exercise Generation Complete --- FinalOutputSchema")
    else:
        print("\n--- Unexpected initial response type ---Unexpected initial response type --- unexpected")

