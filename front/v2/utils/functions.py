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


import time
import re
def process_company(scraped_data, user_input, gemini_model, prompts):
    def safe_api_call(system_prompt, user_prompt):
        """Safely call the Gemini model, handling quota exhaustion (429 errors)."""
        retries = 3  # Retry 3 times for 429 errors
        delay = 60  # Delay in seconds between retries
        for attempt in range(retries):
            try:
                return gemini_model.call_model(system_prompt=system_prompt, user_prompt=user_prompt)
            except Exception as e:
                if "429" in str(e):
                    print(f"DEBUG: Quota exhausted. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                    time.sleep(delay)  # Wait before retrying
                else:
                    raise  # Raise non-429 errors immediately
        print("DEBUG: All retries exhausted. Skipping this company.")
        return "Quota exhausted"

    # Step 1: Interpret scraping
    interpret_system = prompts['interpret_scraping']['system_prompt']
    interpret_user = prompts['interpret_scraping']['user_prompt'].replace("{{scraped_data}}", scraped_data)
    analysis = safe_api_call(interpret_system, interpret_user)

    # Step 2: Generate sales leads
    leads_system = prompts['generate_leads']['system_prompt']
    leads_user = prompts['generate_leads']['user_prompt'] \
        .replace("{{analysis}}", analysis) \
        .replace("{{user_input}}", user_input)
    sales_leads = safe_api_call(leads_system, leads_user)

    # Step 3: Generate partnership probability
    probability_system = prompts['generate_probability']['system_prompt']
    probability_user = prompts['generate_probability']['user_prompt'] \
        .replace("{{analysis}}", analysis) \
        .replace("{{user_input}}", user_input)
    partnership_probability = safe_api_call(probability_system, probability_user)

    # Extract numeric probability for sorting and display
    def extract_probability(text):
        try:
            match = re.search(r'\b(\d{1,3})\b', text)
            if match:
                probability = int(match.group(1))
                return min(max(probability, 0), 100)
        except Exception as e:
            print(f"DEBUG: Failed to extract probability from text: {text}. Error: {e}")
        return 0  # Default to 0 if extraction fails

    probability_value = extract_probability(partnership_probability)

    # Format results for proper HTML rendering
    def format_to_html(text):
        lines = text.splitlines()
        html_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("**") and line.endswith("**"):
                line = f"<b>{line[2:-2]}</b>"
            elif "**" in line:
                line = line.replace("**", "<b>", 1).replace("**", "</b>", 1)
            if line.startswith("I."):
                html_lines.append(f"<li><b>{line}</b></li>")
            elif line.startswith("* **"):
                html_lines.append(f"<ul><li>{line}</li></ul>")
            elif line.startswith("* "):
                html_lines.append(f"<li>{line[2:]}</li>")
            else:
                html_lines.append(f"<p>{line}</p>")
        return f"<ul>{''.join(html_lines)}</ul>"

    analysis_html = f"<b>Analysis:</b>{format_to_html(analysis)}"
    sales_leads_html = f"<b>Sales Leads:</b>{format_to_html(sales_leads)}"
    probability_html = f"<b>Partnership Probability:</b> {probability_value}%"

    return analysis_html, sales_leads_html, probability_html, probability_value
