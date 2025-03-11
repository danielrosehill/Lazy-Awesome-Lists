import os
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv
from src.agent import AwesomeListAgent
from src.config import DEMO_LIST_DIR

# Load environment variables
load_dotenv()

# Create Typer app
app = typer.Typer(help="CLI for creating and editing awesome lists")
console = Console()

@app.command()
def create(
    name: str = typer.Argument(..., help="Name of the awesome list"),
    description: str = typer.Argument(..., help="Description of the awesome list"),
    example: Optional[str] = typer.Option(
        None, "--example", "-e", help="Name of the example to use (without .md extension)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="The model to use for the agent"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", help="OpenAI API key"
    ),
    openrouter_key: Optional[str] = typer.Option(
        None, "--openrouter-key", "-r", help="OpenRouter API key"
    ),
    style: Optional[str] = typer.Option(
        "minimal", "--style", "-s", 
        help="Style of the awesome list (minimal, visual, badges)"
    ),
    community: bool = typer.Option(
        False, "--community", "-c", 
        help="Whether to include community participation guidelines"
    )
):
    """
    Create a new awesome list with the specified parameters.
    """
    # Set API keys if provided
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    if openrouter_key:
        os.environ["OPENROUTER_API_KEY"] = openrouter_key
    
    # Check if API keys are set
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY"):
        console.print(
            Panel(
                "[bold red]Error:[/bold red] No API key provided. Please set either OPENAI_API_KEY or OPENROUTER_API_KEY "
                "environment variable or provide it using the --api-key or --openrouter-key option.",
                title="API Key Required",
                border_style="red"
            )
        )
        raise typer.Exit(1)
    
    # Create agent
    agent = AwesomeListAgent(model=model)
    
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
            result = agent.create_list(user_input, example_name=example)
            
            # Display the result
            console.print("\n[bold green]Result:[/bold green]")
            console.print(Panel(Markdown(result[:500] + "..." if len(result) > 500 else result)))
            
            console.print("\n[bold green]Success![/bold green] Your awesome list has been created.")
            console.print("You can find the full result in the following files:")
            console.print(f"- List: [cyan]{DEMO_LIST_DIR}/awesome-list.md[/cyan]")
            console.print(f"- Starter: [cyan]{DEMO_LIST_DIR}/starter.md[/cyan]")
            
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            raise typer.Exit(1)

@app.command()
def edit(
    edits: str = typer.Argument(..., help="Description of the edits to make"),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="The model to use for the agent"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", help="OpenAI API key"
    ),
    openrouter_key: Optional[str] = typer.Option(
        None, "--openrouter-key", "-r", help="OpenRouter API key"
    )
):
    """
    Edit an existing awesome list with the specified changes.
    """
    # Set API keys if provided
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    if openrouter_key:
        os.environ["OPENROUTER_API_KEY"] = openrouter_key
    
    # Check if API keys are set
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY"):
        console.print(
            Panel(
                "[bold red]Error:[/bold red] No API key provided. Please set either OPENAI_API_KEY or OPENROUTER_API_KEY "
                "environment variable or provide it using the --api-key or --openrouter-key option.",
                title="API Key Required",
                border_style="red"
            )
        )
        raise typer.Exit(1)
    
    # Create agent
    agent = AwesomeListAgent(model=model)
    
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
            raise typer.Exit(1)

@app.command()
def list_examples():
    """
    List all available examples that can be used as templates.
    """
    # Create agent
    agent = AwesomeListAgent()
    
    # Get available examples
    examples = agent.get_available_examples()
    
    # Display the examples
    console.print("\n[bold green]Available Examples:[/bold green]")
    for i, example in enumerate(examples, 1):
        console.print(f"[{i}] {example}")
    
    console.print("\nUse these examples with the 'create' command using the --example option.")
    console.print("Example: [cyan]python main.py create 'My List' 'My Description' --example awesome-android[/cyan]")

@app.command()
def interactive(
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="The model to use for the agent"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", help="OpenAI API key"
    ),
    openrouter_key: Optional[str] = typer.Option(
        None, "--openrouter-key", "-r", help="OpenRouter API key"
    )
):
    """
    Run the awesome list workflow interactively.
    """
    # Set API keys if provided
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    if openrouter_key:
        os.environ["OPENROUTER_API_KEY"] = openrouter_key
    
    # Check if API keys are set
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY"):
        console.print(
            Panel(
                "[bold red]Error:[/bold red] No API key provided. Please set either OPENAI_API_KEY or OPENROUTER_API_KEY "
                "environment variable or provide it using the --api-key or --openrouter-key option.",
                title="API Key Required",
                border_style="red"
            )
        )
        raise typer.Exit(1)
    
    # Create agent
    agent = AwesomeListAgent(model=model)
    
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
    
    # Get user choice
    console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
    console.print("[1] Create a new awesome list")
    console.print("[2] Edit an existing awesome list")
    
    choice = ""
    while choice not in ["1", "2"]:
        choice = console.input("\nEnter your choice (1 or 2): ")
    
    if choice == "1":
        # Get information for creating a new list
        console.print("\n[bold cyan]Let's create a new awesome list![/bold cyan]")
        name = console.input("Enter the name of the awesome list: ")
        description = console.input("Enter a description of the subject: ")
        
        # Get available examples
        examples = agent.get_available_examples()
        console.print("\n[bold cyan]Available Examples:[/bold cyan]")
        for i, example in enumerate(examples, 1):
            console.print(f"[{i}] {example}")
        console.print(f"[{len(examples) + 1}] No example (use default)")
        
        # Get user choice for example
        example_choice = ""
        while not example_choice.isdigit() or int(example_choice) < 1 or int(example_choice) > len(examples) + 1:
            example_choice = console.input(f"\nChoose an example (1-{len(examples) + 1}): ")
        
        example_name = None
        if int(example_choice) <= len(examples):
            example_name = examples[int(example_choice) - 1]
        
        style_options = ["minimal", "visual", "badges"]
        style_choice = ""
        console.print("\nChoose a style for your awesome list:")
        for i, style in enumerate(style_options, 1):
            console.print(f"[{i}] {style.capitalize()}")
        
        while style_choice not in ["1", "2", "3"]:
            style_choice = console.input("\nEnter your choice (1, 2, or 3): ")
        
        style = style_options[int(style_choice) - 1]
        
        community = console.input("\nInclude community participation guidelines? (y/n): ").lower() == "y"
        
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
                raise typer.Exit(1)
    
    else:  # choice == "2"
        # Get information for editing an existing list
        console.print("\n[bold cyan]Let's edit an existing awesome list![/bold cyan]")
        console.print("Please describe the edits you want to make:")
        edits = console.input("> ")
        
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
                raise typer.Exit(1)

if __name__ == "__main__":
    app()