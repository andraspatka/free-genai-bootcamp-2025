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

MAX_STEP_COUNT = 5

console = Console()

memory = AgentMemory()

search_tool = DuckDuckGoSearchTool()
page_content_getter_tool = PageContentGetterTool()
extract_vocabulary_tool = ExtractVocabularyTool()

client = instructor.from_openai(openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"]))

user_language = "English"
foreign_language = "Italian"
number_of_words = 10
song_title = "L'italiano"

system_prompt_generator = SystemPromptGenerator(
    background=[
        f"""
You are a helpful language tutor. You are very good at explaining what foreign words mean and putting them into the appropriate context.
You will help the user understand songs in {foreign_language} by extracting the vocabulary from the song and explaining the meaning of new words.

The user's native language is {user_language}.
The language of the foreign song the user is learning is {foreign_language}.
"""
    ],
    steps=[
        "Search for the song's lyrics on the web", 
        "Get the lyrics", 
        "Extract the vocabulary",
        f"Explain the meaning of {number_of_words} words in simple terms and provide example sentences. Use the user's native language to explain the meaning of new words. \
Focus on words that would be valuable for a language learner. Try to exclude names of people and places",
        "The task is now finished"
    ],
    output_instructions=[
        "Prefix each of your output with either of the following: 'STEP' | 'VOCABULARY' | '/EXIT'",
        "STEP - Intermediate steps taken to get the result",
        "VOCABULARY - The desired result. Output in format: Word: [word] | Meaning: [meaning] | Example: [example] | Example translated: [example translated]",
        "/EXIT - If you have finished the task",
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
       
        agent_message = Text(response.chat_message, style="bold green")
        # if 'VOCABULARY:' in agent_message:
        #     console.print(Text("Result:", style="bold green"), end=" ")
        #     # agent_message = agent_message.replace("VOCABULARY:", "")
        #     console.print(agent_message)
        console.print(Text("DEBUG:", style="bold green"), end=" ")
        console.print(agent_message)
        if step_count == MAX_STEP_COUNT or "EXIT" in response.chat_message:
            break

        response = agent.run(agent.input_schema(chat_message=f"If the task is completed output: /EXIT, otherwise continue"))
        step_count += 1
    

if __name__ == "__main__":
    main()
