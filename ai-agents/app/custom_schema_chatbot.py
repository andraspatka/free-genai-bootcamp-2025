import os
import instructor
import openai
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import List
from pydantic import Field
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema
from atomic_agents.lib.base.base_io_schema import BaseIOSchema

# Initialize a Rich Console for pretty console outputs
console = Console()

# Define a custom output schema
class CustomOutputSchema(BaseIOSchema):
    """Custom schema with chat message and suggested follow-up questions"""
    
    chat_message: str = Field(
        ..., 
        description="The response message from the agent"
    )
    suggested_questions: List[str] = Field(
        ..., 
        description="Suggested follow-up questions for the user"
    )

def create_custom_schema_agent():
    """Create and return an agent with a custom output schema"""
    # Set up OpenAI client with instructor
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = instructor.from_openai(openai.OpenAI(api_key=api_key))
    
    # Initialize memory
    memory = AgentMemory()
    
    # Create a custom system prompt
    system_prompt_generator = SystemPromptGenerator(
        background=[
            "You are a helpful AI assistant that provides useful information.",
            "You suggest relevant follow-up questions after each response."
        ],
        steps=[
            "Understand the user's question or request",
            "Formulate a clear and helpful response",
            "Generate 3 relevant follow-up questions"
        ],
        output_instructions=[
            "Provide clear and concise information",
            "Include 3 suggested follow-up questions that are relevant to the conversation"
        ]
    )
    
    # Create the agent with custom prompt and schema
    agent = BaseAgent(
        config=BaseAgentConfig(
            client=client,
            model="gpt-4o-mini",
            memory=memory,
            system_prompt_generator=system_prompt_generator,
            output_schema=CustomOutputSchema
        )
    )
    
    # Display the system prompt
    console.print(Panel(
        system_prompt_generator.generate_prompt(), 
        title="System Prompt",
        width=console.width, 
        style="bold cyan"
    ))
    
    return agent

def run_chat_loop(agent):
    """Run an interactive chat loop with the agent"""
    console.print(Text("Welcome to the Custom Schema Chatbot!", style="bold green"))
    console.print(Text("This chatbot provides suggested follow-up questions.", style="italic green"))
    console.print(Text("Type '/exit' or '/quit' to end the conversation.\n", style="italic"))
    
    while True:
        user_input = console.input("[bold blue]You:[/bold blue] ")
        if user_input.lower() in ["/exit", "/quit"]:
            console.print("Exiting chat...")
            break
            
        # Create input schema and get response
        input_schema = BaseAgentInputSchema(chat_message=user_input)
        response = agent.run(input_schema)
        
        # Display the agent's response
        console.print(Text("Agent:", style="bold green"), end=" ")
        console.print(Text(response.chat_message, style="green"))
        
        # Display suggested questions
        console.print("\n[bold cyan]Suggested questions:[/bold cyan]")
        for i, question in enumerate(response.suggested_questions, 1):
            console.print(f"[cyan]{i}. {question}[/cyan]")
        console.print()  # Add an empty line for better readability

if __name__ == "__main__":
    try:
        agent = create_custom_schema_agent()
        run_chat_loop(agent)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
