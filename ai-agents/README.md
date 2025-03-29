# Atomic Agents Examples

This project demonstrates how to use the Atomic Agents framework to build various types of AI agents. Atomic Agents is a lightweight, modular framework for building AI agents that focuses on predictability, control, and developer experience.

## Installation

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

## Running the Examples

Run the main script to see all available examples:

```bash
python main.py
```

This will display a menu with the following options:

1. **Simple Chatbot**: Basic implementation with default settings
2. **Custom Prompt Chatbot**: Chatbot with a custom system prompt
3. **Custom Schema Chatbot**: Chatbot with a custom output schema
4. **Context Provider Chatbot**: Chatbot with dynamic context

You can also run each example directly:

```bash
python simple_chatbot.py
python custom_prompt_chatbot.py
python custom_schema_chatbot.py
python context_provider_chatbot.py
```

## Examples Overview

- **Simple Chatbot**: Demonstrates the most basic implementation of an Atomic Agent with default settings.
- **Custom Prompt Chatbot**: Shows how to customize the system prompt to create a specialized agent (in this case, a Python programming assistant).
- **Custom Schema Chatbot**: Illustrates how to define a custom output schema to get structured responses (including suggested follow-up questions).
- **Context Provider Chatbot**: Demonstrates how to inject dynamic context into the agent's system prompt at runtime.

## Framework Resources

- [Atomic Agents GitHub Repository](https://github.com/BrainBlend-AI/atomic-agents)
- [Atomic Agents Documentation](https://brainblend-ai.github.io/atomic-agents/)
- [Overview Video](https://www.youtube.com/watch?v=Sp30YsjGUW0)
- [Quickstart Video](https://www.youtube.com/watch?v=CyZxRU0ax3Q)
