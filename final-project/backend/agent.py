import os
from dotenv import load_dotenv
import logging
from typing import List, Type, Union, Optional

from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.schemas.chat_message import ChatMessage
from atomic_agents.schemas.tool_call import ToolCall, ToolCallResponse
from atomic_agents.systems.agent_system import AgentSystem
from atomic_agents.clients.openai_client import OpenAIClient

from .schemas import (
    AgentInputSchema, AgentOutputSchema, FinalOutputSchema,
    UserInteractionSchema, EvaluationSchema, AgentStateSchema,
    # Import intermediate schemas if needed for explicit flow control
)
from .tool_registry import TOOL_REGISTRY, get_tool_function, get_tool_input_schema
from ..tools.schemas import BaseToolInputSchema, BaseToolOutputSchema # For type hinting

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LanguageExerciseAgent(BaseAgent):
    """Agent responsible for generating language learning exercises based on user requests."""

    def __init__(self, client: Optional[OpenAIClient] = None, agent_system: Optional[AgentSystem] = None):
        super().__init__(
            client=client or OpenAIClient(), # Use provided client or default OpenAI
            agent_system=agent_system or AgentSystem(), # Use provided system or default
            input_schema=AgentInputSchema,
            output_schema=AgentOutputSchema, # Union[UserInteractionSchema, EvaluationSchema, FinalOutputSchema]
            # state_schema=AgentStateSchema # Optional: For complex state management
        )
        logger.info("LanguageExerciseAgent initialized.")
        self._configure_system_prompt()

    def _configure_system_prompt(self):
        """Sets the system prompt for the agent."""
        # Generate tool descriptions for the prompt
        tool_descriptions = "\n".join(
            f"- {name}: {schema.__doc__ or 'No description'}" for name, (_, schema) in TOOL_REGISTRY.items()
        )

        self.agent_system.system_prompt = f"""\
        You are a helpful AI assistant specialized in creating language learning exercises.
        Your goal is to generate an engaging exercise based on the user's specified topic, difficulty, and target language.

        Available Tools:
        {tool_descriptions}

        Exercise Generation Process:
        1.  Analyze the user's request (topic, difficulty, language, context).
        2.  Based on the difficulty, decide on an appropriate exercise type (e.g., translation, listening quiz, image description).
        3.  If necessary, use the available tools to gather information (search, web scrape, YouTube) or generate content (story, image, audio).
        4.  Store generated assets (audio, image) using the S3 tool (implicitly via TTS/TTI tools) and record information (stories, quizzes) in the database using the DB tools.
        5.  Construct the exercise. This might involve:
            - Asking the user to perform a task (translate text, describe an image). Use the `UserInteractionSchema` for this.
            - Presenting a quiz. Use `UserInteractionSchema` (type `present_quiz`) and include quiz details, potentially fetching them via DB tools if generated previously.
            - Simply providing generated content (story, audio) as the exercise. Use `FinalOutputSchema`.
        6.  If the exercise requires user input, you will output a `UserInteractionSchema`. The system will handle getting the user's response.
        7.  If you receive user input (as part of the chat history), evaluate it using your language skills. Output the evaluation using `EvaluationSchema`.
        8.  Once the entire exercise flow is complete (content generated, presented, and potentially evaluated), output the final result using `FinalOutputSchema`.

        Guidelines:
        - Always use the specified target language for the exercise content.
        - Adhere strictly to the requested difficulty level.
        - Use tools step-by-step. Do not try to chain too many actions in one thought.
        - When using tools, provide clear and specific inputs based on the tool's input schema.
        - Reference generated content (e.g., story ID, S3 paths) when creating related items (e.g., quizzes for a story).
        - If you need to ask the user for input, structure your response using `UserInteractionSchema`.
        - If you need to provide feedback on user input, use `EvaluationSchema`.
        - When the task is fully complete, use `FinalOutputSchema`.
        """
        logger.info("System prompt configured.")

    def run(
        self,
        input_data: Union[AgentInputSchema, ChatMessage],
        chat_history: Optional[List[ChatMessage]] = None
    ) -> AgentOutputSchema:
        """Runs the agent to generate or continue an exercise."""
        logger.info(f"Agent run triggered with input type: {type(input_data)}")

        current_chat_history = chat_history.copy() if chat_history else []

        # Handle initial request vs subsequent interaction
        if isinstance(input_data, AgentInputSchema):
            # Start of a new exercise request
            logger.info(f"Starting new exercise generation for topic: {input_data.topic}, difficulty: {input_data.difficulty}")
            initial_message = ChatMessage(role="user", content=f"Generate a {input_data.difficulty} {input_data.target_language} exercise about: {input_data.topic}. Context: {input_data.user_context or 'None'}")
            current_chat_history.append(initial_message)
            # TODO: Optionally initialize state here if using state_schema
        elif isinstance(input_data, ChatMessage):
            # User response to a previous interaction
            logger.info(f"Received user response: {input_data.content[:100]}...")
            current_chat_history.append(input_data)
            # TODO: Retrieve state here if using state_schema
        else:
            logger.error(f"Invalid input type for agent run: {type(input_data)}")
            raise TypeError("Input must be AgentInputSchema or ChatMessage")

        # --- Core Agent Loop (simplified, no explicit state machine here) ---
        # The LLM, guided by the prompt and history, decides the next step:
        # 1. Call a tool
        # 2. Ask the user a question (UserInteractionSchema)
        # 3. Evaluate user response (EvaluationSchema)
        # 4. Finish (FinalOutputSchema)

        agent_response = self.get_response(chat_history=current_chat_history)

        # --- Handle Tool Calls --- (Atomic Agents handles this loop implicitly)
        # The BaseAgent's get_response method handles the tool call loop.
        # We just need to ensure our prompt guides the LLM correctly and
        # the tool registry provides the functions.

        # The final response from get_response will be the Pydantic model (or raw text if parsing fails)
        if isinstance(agent_response.output, (UserInteractionSchema, EvaluationSchema, FinalOutputSchema)):
            logger.info(f"Agent produced valid output schema: {type(agent_response.output).__name__}")
            # TODO: Update state here if using state_schema before returning
            return agent_response.output
        else:
            # Handle cases where the LLM didn't return the expected schema
            logger.warning(f"Agent did not return a recognized output schema. Raw output: {agent_response.output}")
            # Fallback or error handling - maybe try to parse or return a default error state
            # For now, let's raise an error or return a placeholder FinalOutputSchema error
            return FinalOutputSchema(
                exercise_type="Error",
                difficulty="easy", # Placeholder
                text_content=f"Agent failed to produce a valid output. Raw response: {agent_response.output}",
                original_topic="Unknown",
                original_target_language="Unknown"
            )

    def process_tool_calls(self, tool_calls: List[ToolCall]) -> List[ToolCallResponse]:
        """Processes tool calls requested by the LLM."""
        responses = []
        for tool_call in tool_calls:
            logger.info(f"Processing tool call: {tool_call.tool_name} with args: {tool_call.arguments}")
            tool_function = get_tool_function(tool_call.tool_name)
            input_schema = get_tool_input_schema(tool_call.tool_name)

            if tool_function and input_schema:
                try:
                    # Validate and parse arguments using the tool's input schema
                    tool_input = input_schema(**tool_call.arguments)
                    # Execute the tool function
                    tool_output = tool_function(tool_input)
                    # Ensure output is serializable (Pydantic models handle this)
                    output_str = tool_output.model_dump_json()
                    responses.append(ToolCallResponse(tool_call_id=tool_call.tool_call_id, content=output_str))
                    logger.info(f"Tool {tool_call.tool_name} executed successfully.")
                except Exception as e:
                    logger.error(f"Error executing tool {tool_call.tool_name}: {e}", exc_info=True)
                    error_message = f"Error in tool {tool_call.tool_name}: {str(e)}"
                    responses.append(ToolCallResponse(tool_call_id=tool_call.tool_call_id, content=error_message))
            else:
                logger.warning(f"Tool not found or schema missing: {tool_call.tool_name}")
                responses.append(ToolCallResponse(tool_call_id=tool_call.tool_call_id, content=f"Error: Tool '{tool_call.tool_name}' not found."))

        return responses

# Example Usage (typically called from the frontend)
if __name__ == '__main__':
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

