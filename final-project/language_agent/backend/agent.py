import os
import logging
from typing import List, Type, Union, Optional

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig

import instructor
import openai

from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

from language_agent.backend.config import AgentConfig
from language_agent.backend.schemas import AgentInputSchema, AgentOutputSchema
from language_agent.tools import (
    DuckDuckGoSearchTool,
    PageContentGetterTool,
    ExtractVocabularyTool,
    S3UploaderTool,
    S3UploaderToolConfig,
    S3DownloaderTool,
    S3DownloaderToolConfig,
    ImageGeneratorTool,
    ImageGeneratorToolConfig
)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LanguageExerciseAgent(BaseAgent):
    """Agent responsible for generating language learning exercises based on user requests."""

    def __init__(self):
        duckduckgo_search_tool = DuckDuckGoSearchTool()
        page_content_getter_tool = PageContentGetterTool()
        extract_vocabulary_tool = ExtractVocabularyTool()
        s3_uploader_tool = S3UploaderTool(
            S3UploaderToolConfig(
                bucket_name=AgentConfig.s3_bucket,
                aws_access_key_id=AgentConfig.aws_access_key_id,
                aws_secret_access_key=AgentConfig.aws_secret_access_key,
                aws_region=AgentConfig.aws_region
            )
        )
        s3_downloader_tool = S3DownloaderTool(
            S3DownloaderToolConfig(
                aws_access_key_id=AgentConfig.aws_access_key_id,
                aws_secret_access_key=AgentConfig.aws_secret_access_key,
                aws_region=AgentConfig.aws_region
            )
        )
        image_generator_tool = ImageGeneratorTool(
            ImageGeneratorToolConfig(
                openai_api_key=AgentConfig.api_key
            )
        )

        super().__init__(
            BaseAgentConfig(
                client=instructor.from_openai(openai.OpenAI(api_key=AgentConfig.api_key)),
                model=AgentConfig.model,
                tools=[
                    duckduckgo_search_tool,
                    page_content_getter_tool,
                    extract_vocabulary_tool,
                    s3_uploader_tool,
                    s3_downloader_tool,
                    image_generator_tool
                ],
                system_prompt_generator=SystemPromptGenerator(
                    background=[
                        "You are a language teacher specialized in creating interactive and engaging language learning exercises.",
                        "Your goal is to generate an engaging exercise based on the user's specified topic, difficulty, and target language."
                    ],
                    steps=[
                        "Analyze the user's request (topic, difficulty, language, context).",
                        "Based on the difficulty, decide on an appropriate exercise type (e.g., translation, listening quiz, image description).",
                        "If necessary, use the available tools to gather information (search, web scrape) or generate content (story, image).",
                        "Store generated assets (image) using the S3 tool and record information (stories, quizzes) in the database using the DB tools.",
                        "Construct the exercise. This might involve:",
                        "    - Asking the user to perform a task (translate text, describe an image).",
                        "    - Presenting a quiz. If a quiz already exists for the given topic, then fetch the quiz details from the database using the DB tools.",
                        "    - Simply providing generated content (story, image) as the exercise..",
                        "If the exercise requires user input, you will output a `UserInteractionSchema`. The system will handle getting the user's response.",
                        "If you receive user input (as part of the chat history), evaluate it using your language skills. Output the evaluation using `EvaluationSchema`.",
                        "Once the entire exercise flow is complete (content generated, presented, and potentially evaluated), output the final result using `FinalOutputSchema`.",
                    ],
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
        )

        logger.info("LanguageExerciseAgent initialized.")


    def clear_memory(self):
        self.memory.history = []
        self.memory.current_turn_id = None


if __name__ == '__main__':
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    from rich import box
    from rich.progress import Progress, SpinnerColumn, TextColumn

    console = Console()

    
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

    response_msg = response.response_to_user

    while True:
        console.print(f"\n[bold]Agent: {response}[/bold]")
        try:
            user_message = console.input("\n[bold blue]Your question:[/bold blue] ").strip()

            agent_input = AgentInputSchema(
                follow_up=user_message,
                difficulty="none",
                target_language=AgentConfig.target_language,
                topic="",
            )

            if user_message.lower() == "exit":
                console.print("\n[bold]👋 Goodbye![/bold]")
                break
            response_msg = agent.run(agent_input).response_to_user
        
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            console.print("[dim]Please try again or type 'exit' to quit.[/dim]")

