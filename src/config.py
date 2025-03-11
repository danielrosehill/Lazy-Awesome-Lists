import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DEVELOPMENT_DIR = BASE_DIR / "development"
EXAMPLES_DIR = DEVELOPMENT_DIR / "examples"
DEMO_LIST_DIR = BASE_DIR / "demo-list"  # Changed to demo-list in the repo root

# System prompts paths
SYSTEM_PROMPTS_DIR = DEVELOPMENT_DIR / "the-crew" / "system-prompts"
LIST_CREATOR_PROMPT_PATH = SYSTEM_PROMPTS_DIR / "list-creator.md"
LIST_EDITOR_PROMPT_PATH = SYSTEM_PROMPTS_DIR / "list-editor.md"

# List paths (variables used in the prompts)
LIST_PATH = DEMO_LIST_DIR / "awesome-list.md"  # Main list file
LIST_STARTER = DEMO_LIST_DIR / "starter.md"    # Initial draft from creator
LIST_DRAFT = DEMO_LIST_DIR / "draft-edit.md"   # Draft from editor

# Example path (used in the list creator prompt)
DEFAULT_EXAMPLE_PATH = EXAMPLES_DIR / "awesome-android.md"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Model configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

def read_file_content(file_path):
    """Read the content of a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def write_file_content(file_path, content):
    """Write content to a file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)