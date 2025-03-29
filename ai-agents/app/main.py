import os
import instructor
import openai
from rich.text import Text
from rich.console import Console
from rich.panel import Panel
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentOutputSchema

from tools import DuckDuckGoSearchTool, PageContentGetterTool, ExtractVocabularyTool

MAX_STEP_COUNT = 100

console = Console()

memory = AgentMemory()

search_tool = DuckDuckGoSearchTool()
page_content_getter_tool = PageContentGetterTool()
extract_vocabulary_tool = ExtractVocabularyTool()

client = instructor.from_openai(openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"]))

user_language = "English"
foreign_language = "Italian"
song_title = "L'italiano"

system_prompt_generator = SystemPromptGenerator(
    background=[
        f"""
You are a helpful language tutor. You are very good at explaining what foreign words mean and putting them into the appropriate context.
When the user provides a song title, search for the song lyrics and help them learn new vocabulary from it.
First search for the lyrics, then extract vocabulary from them. 
Explain the meaning of new words in simple terms and provide example sentences. 
Use the user's native language to explain the meaning of new words.
Focus on words that would be valuable for a language learner. Try to exclude names of people and places.
The user's native language is {user_language}.
The language of the foreign song the user is learning is {foreign_language}.
"""
    ],
    steps=[
        "Search for the song's lyrics on the web", 
        "Get the lyrics", 
        "Extract the vocabulary",
    ],
    output_instructions=[
        "Output only the following information: Explain the meaning of new words in simple terms and provide example sentences",
        "Use the user's native language to explain the meaning of new words",
        "Format the final answer in the following way: ",
        "VOCABULARY: - Word: [word] | Meaning: [meaning] | Example: [example]",
        "VOCABULARY: - Word: [word] | Meaning: [meaning] | Example: [example]",
        "Once you are done with all steps, output /EXIT",
    ],
)

agent = BaseAgent(
    config=BaseAgentConfig(
        tools=[search_tool, page_content_getter_tool, extract_vocabulary_tool],
        memory=memory,
        model="gpt-4o-mini",
        system_prompt_generator=system_prompt_generator,
        client=client,
    )
)


def main():
    """Main function to run the examples"""
    user_input = console.input("[bold blue]Song you would like to learn about: [/bold blue]")
    step_count = 0
    response = agent.run(agent.input_schema(chat_message=f"help me learn about the song: {user_input}"))
    while True:
        if step_count == MAX_STEP_COUNT or "EXIT" in response.chat_message:
            break
        agent_message = Text(response.chat_message, style="bold green")
        if 'VOCABULARY:' in agent_message:
            console.print(Text("Result:", style="bold green"), end=" ")
            # agent_message = agent_message.replace("VOCABULARY:", "")
            console.print(agent_message)
        console.print(Text("DEBUG:", style="bold green"), end=" ")
        console.print(agent_message)

        response = agent.run(agent.input_schema(chat_message=f"Continue to the next step until /EXIT"))
        step_count += 1
    

if __name__ == "__main__":
    main()
