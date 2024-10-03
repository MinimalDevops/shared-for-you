import os
import shutil

# Define paths
mkdocs_file_path = 'mkdocs-backup.yml'
docs_base_path = 'docs/'
meta_file_path = 'samplefiles/.meta.yml'
index_sample_file_path = 'samplefiles/index_sample.md'
content_sample_file_path = 'samplefiles/contentpage_sample.md'

# Function to create directories, files, and copy .meta.yml and index_sample.md without overwriting
def create_structure_from_md(file_path):
    try:
        # Split the path into folder parts and filename
        parts = file_path.split('/')
        folder_parts, file_name = parts[:-1], parts[-1]

        # Construct the folder path and ensure all necessary directories exist
        folder_path = os.path.join(docs_base_path, *folder_parts)
        
        # Check and create folder if not exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")

        # Ensure .meta.yml is copied to both the folder and subfolders
        for i in range(len(folder_parts)):
            meta_folder = os.path.join(docs_base_path, *folder_parts[:i+1])
            meta_file_target = os.path.join(meta_folder, '.meta.yml')
            if not os.path.exists(meta_file_target):
                shutil.copy(meta_file_path, meta_file_target)
                print(f"Copied .meta.yml to {meta_file_target}")
            else:
                print(f".meta.yml already exists in {meta_folder}")

        # Copy index_sample.md as index.md only in the folder (not subfolders)
        if len(folder_parts) > 0:  # Only for the folder, not subfolder
            folder_index_file = os.path.join(docs_base_path, folder_parts[0], 'index.md')
            if not os.path.exists(folder_index_file):
                # Modify content of index_sample.md to replace # Heading with # folder_name
                with open(index_sample_file_path, 'r') as f:
                    content = f.read().replace("# Heading", f"# {folder_parts[0]}")
                with open(folder_index_file, 'w') as f:
                    f.write(content)
                print(f"Copied and modified index_sample.md as index.md to {folder_index_file}")
            else:
                print(f"index.md already exists in {folder_parts[0]}")

        # Define the full path for the file
        full_file_path = os.path.join(folder_path, file_name)

        # Create the file with the content from contentpage_sample.md
        if not os.path.exists(full_file_path):
            with open(content_sample_file_path, 'r') as content_f:
                content = content_f.read()
            with open(full_file_path, 'w') as f:
                f.write(content)
            print(f"Created file: {full_file_path} with content from {content_sample_file_path}")
        else:
            print(f"File already exists: {full_file_path}")

    except Exception as e:
        print(f"Error while creating structure for {file_path}: {e}")

# Read the mkdocs.yml file as a text file
try:
    with open(mkdocs_file_path, 'r') as f:
        mkdocs_lines = f.readlines()
        print("Reading mkdocs.yml file...")
except FileNotFoundError:
    print(f"Error: {mkdocs_file_path} not found!")
    exit(1)

# Traverse through the lines to find paths ending with .md, excluding 'index.md' and 'tags.md'
for line in mkdocs_lines:
    if line.strip().endswith('.md') and 'index.md' not in line and 'tags.md' not in line:
        # Extract the file path after the colon
        try:
            md_file_path = line.split(':')[-1].strip()
            print(f"Processing .md file path: {md_file_path}")
            create_structure_from_md(md_file_path)
        except Exception as e:
            print(f"Error processing line: {line.strip()} - {e}")

print("Folders, files, and sample files processing complete!")
