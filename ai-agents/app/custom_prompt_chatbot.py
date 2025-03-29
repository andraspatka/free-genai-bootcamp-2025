import os
import instructor
import openai
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema

# Initialize a Rich Console for pretty console outputs
console = Console()

def create_custom_prompt_agent():
    """Create and return an agent with a custom system prompt"""
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
            "You are a helpful AI assistant specializing in Python programming.",
            "You provide clear, concise code examples when appropriate."
        ],
        steps=[
            "Understand the user's programming question or request",
            "Formulate a clear and helpful response",
            "Include code examples when relevant"
        ],
        output_instructions=[
            "Use markdown formatting for code blocks",
            "Explain your code examples clearly"
        ]
    )
    
    # Create the agent with custom prompt
    agent = BaseAgent(
        config=BaseAgentConfig(
            client=client,
            model="gpt-4o-mini",
            memory=memory,
            system_prompt_generator=system_prompt_generator
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
    console.print(Text("Welcome to the Custom Prompt Chatbot!", style="bold green"))
    console.print(Text("This chatbot specializes in Python programming help.", style="italic green"))
    console.print(Text("Type '/exit' or '/quit' to end the conversation.\n", style="italic"))
    
    while True:
        user_input = console.input("[bold blue]You:[/bold blue] ")
        if user_input.lower() in ["/exit", "/quit"]:
            console.print("Exiting chat...")
            break
            
        # Create input schema and get response
        input_schema = BaseAgentInputSchema(chat_message=user_input)
        response = agent.run(input_schema)
        
        console.print(Text("Agent:", style="bold green"), end=" ")
        console.print(Text(response.chat_message, style="green"))
        console.print()  # Add an empty line for better readability

if __name__ == "__main__":
    try:
        agent = create_custom_prompt_agent()
        run_chat_loop(agent)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
