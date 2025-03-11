import os
from openai import OpenAI
from src.config import (
    read_file_content, 
    write_file_content,
    LIST_CREATOR_PROMPT_PATH,
    LIST_EDITOR_PROMPT_PATH,
    DEFAULT_EXAMPLE_PATH,
    LIST_PATH,
    LIST_STARTER,
    LIST_DRAFT,
    DEFAULT_MODEL,
    TEMPERATURE,
    OPENAI_API_KEY,
    OPENROUTER_API_KEY,
    EXAMPLES_DIR
)
from pathlib import Path

class AwesomeListAgent:
    """
    Agent for creating and editing awesome lists.
    Uses OpenAI API directly for simplicity.
    """
    
    def __init__(self, model=None):
        """
        Initialize the agent.
        
        Args:
            model (str, optional): The model to use for the agent
        """
        self.model = model or DEFAULT_MODEL
        self.client = self._get_client()
        
        # Load system prompts
        self.creator_prompt = read_file_content(LIST_CREATOR_PROMPT_PATH)
        self.editor_prompt = read_file_content(LIST_EDITOR_PROMPT_PATH)
        
    def _get_client(self):
        """Get the OpenAI client based on available API keys."""
        # Use OpenRouter if the API key is provided
        if OPENROUTER_API_KEY:
            return OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
        # Otherwise use OpenAI
        elif OPENAI_API_KEY:
            return OpenAI(api_key=OPENAI_API_KEY)
        else:
            raise ValueError("No API key provided for OpenAI or OpenRouter")
    
    def get_available_examples(self):
        """
        Get a list of available examples.
        
        Returns:
            list: List of example names
        """
        examples = []
        for file in os.listdir(EXAMPLES_DIR):
            if file.endswith('.md'):
                examples.append(file.replace('.md', ''))
        return examples
    
    def create_list(self, user_input, example_name=None):
        """
        Create a new awesome list based on the user's input.
        
        Args:
            user_input (str): The user's input describing what they want
            example_name (str, optional): Name of the example to use (without .md extension)
            
        Returns:
            str: The generated awesome list content
        """
        # Determine the example path
        if example_name:
            example_path = EXAMPLES_DIR / f"{example_name}.md"
            if not example_path.exists():
                raise ValueError(f"Example '{example_name}' not found")
        else:
            example_path = DEFAULT_EXAMPLE_PATH
        
        # Read the example content
        example_content = read_file_content(example_path)
        
        # Replace variables in the prompt
        prompt = self.creator_prompt.replace("{{example}}", example_content)
        
        # Call the API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=TEMPERATURE
        )
        
        # Get the response content
        content = response.choices[0].message.content
        
        # Save the content to the starter file
        write_file_content(LIST_STARTER, content)
        write_file_content(LIST_PATH, content)  # Also save to the main list file
        
        return content
    
    def edit_list(self, user_input, list_path=None, draft_path=None):
        """
        Edit an existing awesome list based on the user's input.
        
        Args:
            user_input (str): The user's input describing the edits they want
            list_path (str, optional): Path to the existing awesome list
            draft_path (str, optional): Path to save the edited draft
            
        Returns:
            str: The edited awesome list content
        """
        list_path = list_path or LIST_PATH
        draft_path = draft_path or LIST_DRAFT
        
        # Read the existing list content
        list_content = read_file_content(list_path)
        
        # Replace variables in the prompt
        prompt = self.editor_prompt.replace("{{listpath}}", list_content)
        
        # Call the API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=TEMPERATURE
        )
        
        # Get the response content
        content = response.choices[0].message.content
        
        # Save the content to the draft file
        write_file_content(draft_path, content)
        write_file_content(LIST_PATH, content)  # Also save to the main list file
        
        return content