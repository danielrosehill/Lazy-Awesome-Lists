#!/usr/bin/env python3
"""
Awesome List Creator and Editor

A simple CLI tool for creating and editing awesome lists for GitHub.
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from src.agent import AwesomeListAgent
from src.config import DEMO_LIST_DIR

# Load environment variables
load_dotenv()

# Create console for rich output
console = Console()

# Create history objects for different inputs
name_history = InMemoryHistory()
description_history = InMemoryHistory()
edit_history = InMemoryHistory()

def text_prompt(message, history=None, default=""):
    """
    Display a prompt for text input with editing capabilities.
    
    Args:
        message (str): The message to display
        history (History, optional): History object for this prompt
        default (str, optional): Default value
        
    Returns:
        str: The user's input
    """
    console.print(message, end="")
    return prompt("> ", history=history, default=default)

def check_api_keys():
    """Check if API keys are set and prompt the user if not."""
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY"):
        console.print(
            Panel(
                "[bold yellow]No API key found.[/bold yellow] You need to provide either an OpenAI API key or an OpenRouter API key.",
                title="API Key Required",
                border_style="yellow"
            )
        )
        
        key_type = ""
        while key_type not in ["1", "2"]:
            console.print("\n[bold cyan]Which API key would you like to provide?[/bold cyan]")
            console.print("[1] OpenAI API key")
            console.print("[2] OpenRouter API key")
            key_type = text_prompt("\nEnter your choice (1 or 2)")
        
        if key_type == "1":
            api_key = text_prompt("\nEnter your OpenAI API key")
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            api_key = text_prompt("\nEnter your OpenRouter API key")
            os.environ["OPENROUTER_API_KEY"] = api_key
        
        # Ask if the user wants to save the key to .env
        save_key = text_prompt("\nDo you want to save this key to .env file for future use? (y/n)").lower()
        if save_key == "y":
            key_name = "OPENAI_API_KEY" if key_type == "1" else "OPENROUTER_API_KEY"
            with open(".env", "w") as f:
                f.write(f"{key_name}={api_key}\n")
            console.print("[green]API key saved to .env file.[/green]")

def create_awesome_list(agent):
    """Create a new awesome list."""
    console.print("\n[bold cyan]Let's create a new awesome list![/bold cyan]")
    name = text_prompt("Enter the name of the awesome list", history=name_history)
    description = text_prompt("Enter a description of the subject", history=description_history)
    
    # Get available examples
    examples = agent.get_available_examples()
    console.print("\n[bold cyan]Available Examples:[/bold cyan]")
    for i, example in enumerate(examples, 1):
        console.print(f"[{i}] {example}")
    console.print(f"[{len(examples) + 1}] No example (use default)")
    
    # Get user choice for example
    example_choice = ""
    while not example_choice.isdigit() or int(example_choice) < 1 or int(example_choice) > len(examples) + 1:
        example_choice = text_prompt(f"\nChoose an example (1-{len(examples) + 1})")
    
    example_name = None
    if int(example_choice) <= len(examples):
        example_name = examples[int(example_choice) - 1]
    
    style_options = ["minimal", "visual", "badges"]
    style_choice = ""
    console.print("\nChoose a style for your awesome list:")
    for i, style in enumerate(style_options, 1):
        console.print(f"[{i}] {style.capitalize()}")
    
    while style_choice not in ["1", "2", "3"]:
        style_choice = text_prompt("\nEnter your choice (1, 2, or 3)")
    
    style = style_options[int(style_choice) - 1]
    
    community = text_prompt("\nInclude community participation guidelines? (y/n)").lower() == "y"
    
    # Construct user input
    user_input = (
        f"Create an awesome list named '{name}' about {description}. "
        f"Use a {style} style. "
    )
    
    if community:
        user_input += "Include guidelines for community participation."
    
    # Show processing message
    with console.status("[bold green]Creating your awesome list...[/bold green]", spinner="dots"):
        try:
            # Create the list with the specified example
            result = agent.create_list(user_input, example_name=example_name)
            
            # Display the result
            console.print("\n[bold green]Result:[/bold green]")
            console.print(Panel(Markdown(result[:500] + "..." if len(result) > 500 else result)))
            
            console.print("\n[bold green]Success![/bold green] Your awesome list has been created.")
            console.print("You can find the full result in the following files:")
            console.print(f"- List: [cyan]{DEMO_LIST_DIR}/awesome-list.md[/cyan]")
            console.print(f"- Starter: [cyan]{DEMO_LIST_DIR}/starter.md[/cyan]")
            
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            sys.exit(1)

def edit_awesome_list(agent):
    """Edit an existing awesome list."""
    console.print("\n[bold cyan]Let's edit an existing awesome list![/bold cyan]")
    console.print("Please describe the edits you want to make:")
    edits = text_prompt("", history=edit_history)
    
    # Show processing message
    with console.status("[bold green]Editing your awesome list...[/bold green]", spinner="dots"):
        try:
            # Edit the list
            result = agent.edit_list(edits)
            
            # Display the result
            console.print("\n[bold green]Result:[/bold green]")
            console.print(Panel(Markdown(result[:500] + "..." if len(result) > 500 else result)))
            
            console.print("\n[bold green]Success![/bold green] Your awesome list has been updated.")
            console.print("You can find the full result in the following files:")
            console.print(f"- List: [cyan]{DEMO_LIST_DIR}/awesome-list.md[/cyan]")
            console.print(f"- Draft: [cyan]{DEMO_LIST_DIR}/draft-edit.md[/cyan]")
            
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            sys.exit(1)

def list_examples(agent):
    """List all available examples."""
    # Get available examples
    examples = agent.get_available_examples()
    
    # Display the examples
    console.print("\n[bold green]Available Examples:[/bold green]")
    for i, example in enumerate(examples, 1):
        console.print(f"[{i}] {example}")

def main():
    """Main function to run the awesome list workflow."""
    # Ensure the necessary directories exist
    os.makedirs(DEMO_LIST_DIR, exist_ok=True)
    
    # Welcome message
    console.print(
        Panel(
            "Welcome to the [bold green]Awesome List Creator[/bold green]!\n\n"
            "This tool helps you create and edit awesome lists for GitHub.\n"
            "You can create a new list from scratch or edit an existing one.",
            title="Awesome List Creator",
            border_style="green"
        )
    )
    
    # Check if API keys are set
    check_api_keys()
    
    # Create agent
    agent = AwesomeListAgent()
    
    while True:
        # Main menu
        console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
        console.print("[1] Create a new awesome list")
        console.print("[2] Edit an existing awesome list")
        console.print("[3] List available examples")
        console.print("[4] Exit")
        
        choice = ""
        while choice not in ["1", "2", "3", "4"]:
            choice = text_prompt("\nEnter your choice (1-4)")
        
        if choice == "1":
            create_awesome_list(agent)
        elif choice == "2":
            edit_awesome_list(agent)
        elif choice == "3":
            list_examples(agent)
        else:  # choice == "4"
            console.print("\n[bold green]Thank you for using Awesome List Creator![/bold green]")
            sys.exit(0)
        
        # Ask if the user wants to continue
        continue_choice = text_prompt("\nDo you want to perform another action? (y/n)").lower()
        if continue_choice != "y":
            console.print("\n[bold green]Thank you for using Awesome List Creator![/bold green]")
            break

if __name__ == "__main__":
    main()