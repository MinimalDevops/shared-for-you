import os
import re
import yaml

def load_yaml_keys(yaml_file_path):
    """Load the keys from a YAML file."""
    with open(yaml_file_path, 'r') as file:
        keys = yaml.safe_load(file)
    return keys

def replace_words_in_file(file_path, keys):
    """Replace words in the .md file by wrapping keys in double curly brackets,
    but skip replacements if the word is inside any type of bracket until the corresponding closing bracket is found."""
    
    with open(file_path, 'r') as file:
        content = file.read()

    # Regex pattern to identify opening and closing brackets
    opening_brackets = re.compile(r'(\{\{|\[\[|\(|\[)')
    closing_brackets = {
        '{{': '}}',
        '[[': ']]',
        '(': ')',
        '[': ']'
    }

    # Function to handle replacement, only if not within brackets
    def replacer(match, within_brackets):
        word = match.group(0)
        # Only replace if the flag (within_brackets) is False
        if not within_brackets:
            return f'{{{{{word.lower()}}}}}'  # Replace with {{word}}
        return word  # If inside brackets, return the word unchanged

    within_brackets = False
    bracket_type = None

    # Process each word in the content
    new_content = ""
    index = 0
    while index < len(content):
        char = content[index]

        # Check for opening brackets
        match = opening_brackets.match(content[index:])
        if match:
            within_brackets = True
            bracket_type = match.group(0)  # Save the type of opening bracket
            new_content += match.group(0)
            index += len(match.group(0))
            continue

        # If within brackets, check for corresponding closing bracket
        if within_brackets and content[index:].startswith(closing_brackets[bracket_type]):
            within_brackets = False  # Found the closing bracket, reset the flag
            new_content += closing_brackets[bracket_type]
            index += len(closing_brackets[bracket_type])
            continue

        # If not within brackets, apply the replacement logic for keys
        for key in keys:
            pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
            match = pattern.match(content[index:])
            if match:
                new_content += replacer(match, within_brackets)
                index += len(match.group(0))
                break
        else:
            # Add characters not affected by key replacement
            new_content += char
            index += 1

    # Save the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(new_content)

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
