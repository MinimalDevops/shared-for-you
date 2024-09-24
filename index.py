import os

# Root folder where scanning starts
root_dir = 'docs/'

# Folders to ignore
ignored_folders = {'images', 'assets', 'blog'}

def generate_wikilink(md_file_path):
    # Generate wikilink in the format: [[Name_of_MD_file_without_extension | Title_from_first_line]]
    try:
        with open(md_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith('# '):  # Find the first line starting with '# '
                    title = line[2:].strip()  # Remove "# " from the beginning
                    break
            else:
                title = "No title found"  # If no line with '# ' is found
    except Exception as e:
        print(f"Error reading file {md_file_path}: {e}")
        title = "Error reading title"
    
    # Extract the file name without the extension for the wikilink
    md_file_name = os.path.splitext(os.path.basename(md_file_path))[0]
    return f"- [[{md_file_name}|{title}]]\n"

def generate_index_for_directory(dir_path, folder_name):
    # Path to the index.md file in the current directory
    index_path = os.path.join(dir_path, 'index.md')

    # Read the first line of an existing index.md if it exists and starts with '# '
    preserved_line = ""
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as existing_index_file:
            first_line = existing_index_file.readline().strip()
            if first_line.startswith('# '):
                preserved_line = first_line + '\n\n'  # Keep the first line and add two line breaks

    # Get all the files and folders in the current directory
    entries = sorted(os.listdir(dir_path))
    
    # Start with the preserved first line if available, otherwise default to "# folder_name" if empty
    index_content = preserved_line if preserved_line else f"# {folder_name}\n\n"

    # Separate files and folders
    folders = [entry for entry in entries if os.path.isdir(os.path.join(dir_path, entry))]
    md_files = [entry for entry in entries if entry.endswith('.md') and entry != 'index.md']

    # Create bullet points for markdown files in the current directory
    for md_file in md_files:
        md_file_path = os.path.join(dir_path, md_file)
        index_content += generate_wikilink(md_file_path)

    # Recursively find markdown files in subdirectories
    for folder in folders:
        subfolder_path = os.path.join(dir_path, folder)
        for subdir, _, sub_md_files in os.walk(subfolder_path):
            for sub_md_file in sub_md_files:
                if sub_md_file.endswith('.md') and sub_md_file != 'index.md':
                    sub_md_file_path = os.path.join(subdir, sub_md_file)
                    index_content += generate_wikilink(sub_md_file_path)

    # Save the updated content in index.md, preserving the first line
    with open(index_path, 'w', encoding='utf-8') as index_file:
        index_file.write(index_content)

def generate_indexes_for_subdirectories_of_docs(root_dir, ignored_folders):
    # Only generate index.md for immediate subfolders of docs/, ignoring specified folders
    for folder_name in sorted(os.listdir(root_dir)):
        folder_path = os.path.join(root_dir, folder_name)
        if os.path.isdir(folder_path) and folder_name not in ignored_folders:  # Only process non-ignored directories
            generate_index_for_directory(folder_path, folder_name)

if __name__ == '__main__':
    generate_indexes_for_subdirectories_of_docs(root_dir, ignored_folders)
