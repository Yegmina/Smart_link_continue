import json
import yaml
import os
from .gemini import GeminiModel


def load_prompts(prompt_file="utils/ai/prompts.yaml"):
    """
    Load YAML prompts for AI processing.

    Args:
        prompt_file (str): Relative path to the YAML file.

    Returns:
        dict: A dictionary containing the prompts.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
        yaml.YAMLError: If there is an error in parsing the YAML file.
    """
    try:
        # Construct the absolute path to the prompts.yaml file
        base_dir = os.getcwd()  # Get current working directory
        sub_dir = os.path.join(base_dir, "utils", "ai")  # Explicitly define the subdirectory
        file_name = "prompts.yaml"  # File name

        # Combine the components into the full path
        prompt_file_path = os.path.join(sub_dir, file_name)
        print(f"DEBUG: Attempting to load prompts from {prompt_file_path}")

        # Check if the file exists
        if not os.path.exists(prompt_file_path):
            raise FileNotFoundError(f"Prompt file not found at {prompt_file_path}")

        # Load the YAML file
        with open(prompt_file_path, "r", encoding="utf-8") as file:
            prompts = yaml.safe_load(file)
            return prompts
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}") from e

def load_scraped_companies(file_path="data/scraped_companies.json"):
    """
    Load the scraped companies JSON file from the data directory.
    """
    try:
        full_path = os.path.join(os.getcwd(), file_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON file {file_path}: {e}")


def process_company(scraped_data, gemini_model, prompts):
    interpret_system = prompts['interpret_scraping']['system_prompt']
    interpret_user = prompts['interpret_scraping']['user_prompt'].replace("{{scraped_data}}", scraped_data)
    analysis = gemini_model.call_model(user_prompt=interpret_user, system_prompt=interpret_system)

    leads_system = prompts['generate_leads']['system_prompt']
    leads_user = prompts['generate_leads']['user_prompt'].replace("{{analysis}}", analysis)
    sales_leads = gemini_model.call_model(user_prompt=leads_user, system_prompt=leads_system)

    # Format the analysis and sales leads for proper HTML rendering
    def format_to_html(text):
        lines = text.splitlines()
        html_lines = []
        for line in lines:
            line = line.strip()  # Trim leading/trailing spaces
            if not line:  # Skip empty lines
                continue

            # Handle bold formatting
            if line.startswith("**") and line.endswith("**"):
                line = f"<b>{line[2:-2]}</b>"
            elif "**" in line:  # Bold key-value pairs like "**Key:** Value"
                line = line.replace("**", "<b>", 1).replace("**", "</b>", 1)

            # Identify list hierarchy
            if line.startswith("I."):  # Main numbered list
                html_lines.append(f"<li><b>{line}</b></li>")
            elif line.startswith("* **"):  # Nested bold list item
                html_lines.append(f"<ul><li>{line}</li></ul>")
            elif line.startswith("* "):  # Simple bullet list
                html_lines.append(f"<li>{line[2:]}</li>")
            else:  # Plain text
                html_lines.append(f"<p>{line}</p>")

        return f"<ul>{''.join(html_lines)}</ul>"

    analysis_html = f"<b>Analysis:</b>{format_to_html(analysis)}"
    sales_leads_html = f"<b>Sales Leads:</b>{format_to_html(sales_leads)}"

    return analysis_html, sales_leads_html

"""def load_prompts(prompt_file="prompts.yaml"):
    with open(prompt_file, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)"""