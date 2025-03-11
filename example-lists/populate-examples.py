#!/usr/bin/env python3
import os
import re
import requests
from pathlib import Path
from urllib.parse import urlparse

def parse_github_url(url):
    """
    Parse a GitHub URL to extract owner and repository name.
    
    Supports formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo/
    - https://github.com/owner/repo/blob/branch/README.md
    - git@github.com:owner/repo.git
    """
    # Handle SSH URLs
    if url.startswith("git@github.com:"):
        path = url.split("git@github.com:")[1]
        if path.endswith(".git"):
            path = path[:-4]
        parts = path.split("/")
        return parts[0], parts[1]
    
    # Handle HTTPS URLs
    parsed_url = urlparse(url)
    if parsed_url.netloc != "github.com" and not parsed_url.netloc.endswith(".github.com"):
        raise ValueError(f"Not a GitHub URL: {url}")
    
    path_parts = [p for p in parsed_url.path.split("/") if p]
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitHub repository URL: {url}")
    
    owner, repo = path_parts[0], path_parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    
    return owner, repo

def get_readme_content(owner, repo):
    """
    Fetch README content from a GitHub repository.
    First tries README.md, then falls back to readme.md if not found.
    """
    # Try README.md first (most common)
    readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
    response = requests.get(readme_url)
    
    # If not found, try master branch
    if response.status_code != 200:
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
        response = requests.get(readme_url)
    
    # If still not found, try lowercase readme.md
    if response.status_code != 200:
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/readme.md"
        response = requests.get(readme_url)
    
    # Try lowercase on master branch
    if response.status_code != 200:
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/readme.md"
        response = requests.get(readme_url)
    
    if response.status_code != 200:
        raise ValueError(f"Could not find README for {owner}/{repo}")
    
    return response.text

def save_readme(content, repo_name, output_dir="examples"):
    """
    Save README content to a file in the specified directory.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename based on repo name
    filename = f"{repo_name}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Write content to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath

def process_github_url(url, output_dir="examples"):
    """
    Process a GitHub URL: parse it, fetch README, and save it.
    Returns a tuple of (success, message).
    """
    try:
        # Parse GitHub URL
        owner, repo = parse_github_url(url)
        print(f"Fetching README for {owner}/{repo}...")
        
        # Get README content
        readme_content = get_readme_content(owner, repo)
        
        # Save README to file
        output_file = save_readme(readme_content, repo, output_dir)
        return True, f"SUCCESS: README saved to {output_file}"
        
    except Exception as e:
        return False, f"ERROR: {str(e)}"

def main():
    print("=== GitHub README Downloader ===")
    print("This script downloads README files from GitHub repositories")
    print("and saves them to the 'examples' directory.")
    print("Enter 'exit', 'quit', or press Ctrl+C to exit.")
    print()
    
    while True:
        # Get GitHub URL from user
        url = input("Enter GitHub repository URL (or 'exit' to quit): ").strip()
        
        # Check if user wants to exit
        if url.lower() in ['exit', 'quit', 'q', '']:
            print("Exiting. Goodbye!")
            break
        
        # Process the URL
        success, message = process_github_url(url)
        print(message)
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")