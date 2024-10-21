import os
from pathlib import Path
from datetime import datetime

# Get the absolute path of the current script's directory
current_dir = Path(__file__).parent.resolve()

# Folder to scan for markdown files
folder_path = (current_dir / "../../docs/").resolve()  # Resolves to absolute path
output_path = (current_dir / "../../docs/index.md").resolve()  # Resolves to absolute path
home_file_path = (current_dir / "../../samplefiles/home.md").resolve()  # Resolves to absolute path

# Function to get the heading from the .md file (first line that starts with "#")
def get_heading(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            # Check if the line starts with a single "# " (indicating a heading)
            if line.startswith("# "):
                # Remove the "#" and return the heading text
                return line[2:].strip()
    return "No heading"

# Get list of all .md files (excluding index.md) with modification times
def get_md_files(folder_path):
    md_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".md") and file != "index.md":
                file_path = os.path.join(root, file)
                mod_time = os.path.getmtime(file_path)
                md_files.append((file_path, mod_time))
    return md_files

# Sort files by modification time in descending order and get top 5
def get_top_md_files(md_files, top_n=5):
    md_files.sort(key=lambda x: x[1], reverse=True)
    return md_files[:top_n]

# Generate markdown list of top 5 files with format [[Name_of_md_file|Heading]]
def generate_markdown(top_md_files):
    lines = []
    for i, (file_path, mod_time) in enumerate(top_md_files, start=1):
        file_name = Path(file_path).stem  # Remove .md extension
        heading = get_heading(file_path)
        lines.append(f"{i}. [[{file_name}|{heading}]]")
    return lines

# Read content from home.md
def read_home_content(home_file_path):
    with open(home_file_path, "r", encoding="utf-8") as f:
        return f.read()

# Write content to index.md, starting with home.md content and then appending new markdown
def write_to_index_md(home_content, markdown_lines, output_path="docs/index.md"):
    with open(output_path, "w", encoding="utf-8") as f:  # Open in write mode to overwrite existing content
        f.write(home_content)  # Write the home.md content first
        f.write("\n# Latest Modified Files\n\n")
        f.write("\n".join(markdown_lines))
        f.write("\n")

# Main function to execute the script
def main():
    # Read the content from home.md
    home_content = read_home_content(home_file_path)
    
    # Get the list of .md files and their modification times
    md_files = get_md_files(folder_path)
    
    # Get the top 5 most recently modified files
    top_md_files = get_top_md_files(md_files)
    
    # Generate the markdown for the top 5 files
    markdown_lines = generate_markdown(top_md_files)
    
    # Write the final output to docs/index.md
    write_to_index_md(home_content, markdown_lines)

if __name__ == "__main__":
    main()
