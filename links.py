
import os
import re
import yaml

def load_yaml_keys(yaml_file_path):
    """Load the keys from a YAML file."""
    with open(yaml_file_path, 'r') as file:
        keys = yaml.safe_load(file)
    return keys

def replace_words_in_file(file_path, keys):
    """Replace words in the .md file by wrapping keys in double curly brackets, but skip replacements inside {{}} or with spaces around {{ }}."""
    with open(file_path, 'r') as file:
        content = file.read()

    # Regex pattern to match anything between double curly brackets, accounting for possible spaces
    skip_pattern = re.compile(r'\{\{\s*.*?\s*\}\}')

    # Function to handle replacement, skipping content inside {{ }}
    def replacer(match):
        word = match.group(0)
        # Check if the word is inside double curly brackets
        if skip_pattern.search(content, match.start() - 3, match.end() + 3):
            return word  # Don't replace if found inside or near {{ }}
        return f'{{{{{word.lower()}}}}}'

    for key in keys:
        # Case-insensitive word replacement, wrapping the key in double curly brackets
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        content = pattern.sub(replacer, content)

    # Save the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(content)

def process_markdown_files(directory, keys):
    """Recursively go through all .md files in the given directory and replace keys."""
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.md'):
                file_path = os.path.join(root, file_name)
                replace_words_in_file(file_path, keys)

if __name__ == "__main__":
    # Define the path to the YAML file and the directory containing .md files
    yaml_file_path = "docs/assets/yaml/macro1.yml"
    directory_path = "docs/"  

    # Load the keys from the YAML file
    keys = load_yaml_keys(yaml_file_path)

    # Start processing the markdown files with key replacements
    process_markdown_files(directory_path, keys)
    

  