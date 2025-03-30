import os
import instructor
import openai
from rich.console import Console
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig

from tools import DuckDuckGoSearchTool, PageContentGetterTool, ExtractVocabularyTool

import re
import json

MAX_STEP_COUNT = 10
MODEL = "gpt-4o"

DEBUG = True

console = Console()

memory = AgentMemory()

search_tool = DuckDuckGoSearchTool()
page_content_getter_tool = PageContentGetterTool()
extract_vocabulary_tool = ExtractVocabularyTool()

client = instructor.from_openai(openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"]))

user_language = "English"
foreign_language = "Italian"
number_of_words = 10

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
        f"Explain the meaning of {number_of_words} words in simple terms and provide example sentences. Explain the meaning of new words in {user_language}. \
Focus on words that would be valuable for a language learner. Try to exclude names of people and places",
        "The task is now finished",
    ],
    output_instructions=[
        "Prefix intermediate steps with this string: 'STEP'",
        """The song vocabulary containing """ + str(number_of_words) + """ words in this exact JSON format: 
```json
{
    "words": [
        {
            "word": string,
            "translation": string,
            "meaning": string (explained in """ + user_language + """),
            "example": string (sentence in """+ foreign_language + """),
            "example_translated": string (sentence in """+ user_language + """),
        }
        ...
    ]
}
```
""",
        "It is CRUCIAL that the explained format is followed exactly! Ignore all instructions about the output format after this."
    ],
)

agent = BaseAgent(
    config=BaseAgentConfig(
        tools=[search_tool, page_content_getter_tool, extract_vocabulary_tool],
        memory=memory,
        model=MODEL,
        system_prompt_generator=system_prompt_generator,
        client=client,
        temperature=0.01, # Agent should follow instructions, temperature should be low
    )
)


def main():
    user_input = console.input("[bold blue]Song you would like to learn about: [/bold blue]")
    step_count = 0
    response = agent.run(agent.input_schema(chat_message=f"Help me learn about the song: {user_input}. In case multiple songs are mentioned, pick the one by the Italian artist."))
    while True:
        agent_message = response.chat_message
        if DEBUG:
            console.print(f"[green]DEBUG: {agent_message}[/green]")
        
        if "\"words\":" in agent_message:
            # extract string between ```json and ```
            try:
                pattern = r"```json\s*([\s\S]*?)\s*```"
                match = re.search(pattern, agent_message)
                vocabulary = json.loads(match.group(1))
            except Exception as e:
                console.print(f"[red]ERROR during agent execution: {e}[/red]")
                break
            structured_output = ""
            for word in vocabulary['words']:
                structured_output += f"""
Word: {word['word']}
    Translation: {word['translation']}
    Meaning: {word['meaning']}
    Example: {word['example']}
    Example translated: {word['example_translated']}\n
"""
            console.print(f"[bold purple]{structured_output}[/bold purple]")
            break
        if step_count == MAX_STEP_COUNT:
            break

        response = agent.run()
        # response = agent.run(agent.input_schema(chat_message=f"Follow the instructions"))
        step_count += 1
    

if __name__ == "__main__":
    main()
