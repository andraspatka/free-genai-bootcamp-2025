import os
import instructor
import openai
from rich.console import Console
from rich.text import Text
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema

# Initialize a Rich Console for pretty console outputs
console = Console()

def create_simple_agent():
    """Create and return a simple agent with default settings"""
    # Set up OpenAI client with instructor
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = instructor.from_openai(openai.OpenAI(api_key=api_key))
    
    # Initialize memory
    memory = AgentMemory()
    
    # Create the agent
    agent = BaseAgent(
        config=BaseAgentConfig(
            client=client,
            model="gpt-4o-mini",  # You can use other models as well
            memory=memory
        )
    )
    
    return agent

def run_chat_loop(agent):
    """Run an interactive chat loop with the agent"""
    console.print(Text("Welcome to the Simple Chatbot!", style="bold green"))
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
        agent = create_simple_agent()
        run_chat_loop(agent)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
