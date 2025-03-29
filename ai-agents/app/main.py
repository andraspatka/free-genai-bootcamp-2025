import os
from rich.console import Console
from rich.panel import Panel

console = Console()

def check_api_key():
    """Check if the OpenAI API key is set"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] OPENAI_API_KEY environment variable is not set")
        console.print("Please set your OpenAI API key with:")
        console.print("[bold]export OPENAI_API_KEY='your-api-key'[/bold]")
        return False
    return True

def display_menu():
    """Display the menu of available chatbots"""
    console.print(Panel(
        """[bold]Atomic Agents Examples[/bold]
        
1. Simple Chatbot - Basic implementation with default settings
2. Custom Prompt Chatbot - Chatbot with a custom system prompt
3. Custom Schema Chatbot - Chatbot with a custom output schema
4. Context Provider Chatbot - Chatbot with dynamic context
5. Exit
        """,
        title="Menu",
        width=60
    ))
    
    choice = console.input("[bold]Enter your choice (1-5):[/bold] ")
    return choice

def main():
    """Main function to run the examples"""
    if not check_api_key():
        return
    
    while True:
        choice = display_menu()
        
        if choice == "1":
            console.clear()
            console.print("[bold]Running Simple Chatbot...[/bold]\n")
            from simple_chatbot import create_simple_agent, run_chat_loop
            agent = create_simple_agent()
            run_chat_loop(agent)
            
        elif choice == "2":
            console.clear()
            console.print("[bold]Running Custom Prompt Chatbot...[/bold]\n")
            from custom_prompt_chatbot import create_custom_prompt_agent, run_chat_loop
            agent = create_custom_prompt_agent()
            run_chat_loop(agent)
            
        elif choice == "3":
            console.clear()
            console.print("[bold]Running Custom Schema Chatbot...[/bold]\n")
            from custom_schema_chatbot import create_custom_schema_agent, run_chat_loop
            agent = create_custom_schema_agent()
            run_chat_loop(agent)
            
        elif choice == "4":
            console.clear()
            console.print("[bold]Running Context Provider Chatbot...[/bold]\n")
            from context_provider_chatbot import create_context_provider_agent, run_chat_loop
            agent = create_context_provider_agent()
            run_chat_loop(agent)
            
        elif choice == "5":
            console.print("[bold]Exiting...[/bold]")
            break
            
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

if __name__ == "__main__":
    main()
