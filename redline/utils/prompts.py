import os

def load_prompt(prompt_name: str, base_path: str = "redline/prompts") -> str:
    """
    Loads a prompt from the existing prompts directory.
    prompt_name should be the filename without the path.
    """
    # Adjust path if we are running from cloud_build/
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    file_path = os.path.join(repo_root, base_path, prompt_name)
    
    if not os.path.exists(file_path):
        # Try without extension or with .md
        if not file_path.endswith(".md"):
            file_path += ".md"
            
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return ""

def list_available_prompts(base_path: str = "redline/prompts") -> list:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    target_path = os.path.join(repo_root, base_path)
    if os.path.exists(target_path):
        return [f for f in os.listdir(target_path) if f.endswith(".md")]
    return []

