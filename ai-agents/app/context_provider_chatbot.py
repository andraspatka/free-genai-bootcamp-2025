import os
import instructor
import openai
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema

# Initialize a Rich Console for pretty console outputs
console = Console()

# Create a custom context provider
class WeatherProvider(SystemPromptContextProviderBase):
    def __init__(self, title: str, weather_data: dict):
        super().__init__(title=title)
        self.weather_data = weather_data
        
    def get_info(self) -> str:
        return (f"Current temperature: {self.weather_data['temperature']}°C\n"
                f"Conditions: {self.weather_data['conditions']}\n"
                f"Humidity: {self.weather_data['humidity']}%\n"
                f"Wind: {self.weather_data['wind']} km/h")

def create_context_provider_agent():
    """Create and return an agent with a context provider"""
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
            "You are a helpful AI assistant that provides information and recommendations.",
            "You have access to current weather data that you can use to enhance your responses."
        ],
        steps=[
            "Understand the user's question or request",
            "Consider the current weather information when relevant",
            "Formulate a clear and helpful response"
        ],
        output_instructions=[
            "Provide clear and concise information",
            "When appropriate, reference the current weather in your responses",
            "Suggest activities or recommendations based on the weather when relevant"
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
    
    # Create and register the weather context provider
    weather_provider = WeatherProvider(
        title="Current Weather",
        weather_data={
            "temperature": 22,
            "conditions": "Sunny",
            "humidity": 45,
            "wind": 10
        }
    )
    
    # Register with the agent
    agent.register_context_provider("weather", weather_provider)
    
    # Display the system prompt with context
    console.print(Panel(
        system_prompt_generator.generate_prompt(), 
        title="System Prompt with Context",
        width=console.width, 
        style="bold cyan"
    ))
    
    return agent

def run_chat_loop(agent):
    """Run an interactive chat loop with the agent"""
    console.print(Text("Welcome to the Context Provider Chatbot!", style="bold green"))
    console.print(Text("This chatbot has access to current weather information.", style="italic green"))
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
        agent = create_context_provider_agent()
        run_chat_loop(agent)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
