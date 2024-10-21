
# README

## Overview

This Python script scans a specified folder for markdown (`.md`) files, identifies the top 5 most recently modified files, extracts their headings, and generates an `index.md` file that lists these files with their headings. The script also includes content from a `home.md` file as a prelude to the generated list.

## Features

- **Markdown File Scanning**: The script recursively scans the specified folder (`../../docs/`) for all markdown files, excluding `index.md`.
- **Sorting by Modification Date**: It retrieves the modification times of the files and sorts them in descending order, picking the top 5 most recently modified files.
- **Heading Extraction**: For each markdown file, the script extracts the first heading (the first line that starts with a `#`).
- **Markdown List Generation**: It creates a markdown list that includes the top 5 files, formatted as `[[FileName|Heading]]`.
- **Home Content Inclusion**: The script includes content from a separate `home.md` file and appends the generated list of top files beneath this content.
- **Index File Creation**: The result is written to a new `index.md` file in the target directory, overwriting any existing content.

## File Structure

- `../../docs/`: The folder that contains the markdown files to be scanned.
- `../../samplefiles/home.md`: The file whose content is used as a prelude in the `index.md`.
- `../../docs/index.md`: The file where the result is written, combining the content from `home.md` and the list of top 5 files.

## Functions

### `get_heading(file_path)`
- Reads the specified markdown file and returns the first heading found (line starting with `#`).
- Returns `"No heading"` if no valid heading is found.

### `get_md_files(folder_path)`
- Scans the `folder_path` recursively for all `.md` files, excluding `index.md`.
- Returns a list of tuples with the file path and its last modification time.

### `get_top_md_files(md_files, top_n=5)`
- Sorts the list of markdown files by their modification time in descending order.
- Returns the top `n` files, where `n` defaults to 5.

### `generate_markdown(top_md_files)`
- Generates markdown formatted lines for the top `n` markdown files in the format `[[FileName|Heading]]`.

### `read_home_content(home_file_path)`
- Reads the content of the `home.md` file and returns it as a string.

### `write_to_index_md(home_content, markdown_lines, output_path)`
- Writes the content of `home.md` followed by the markdown list of top files to the specified `output_path` (which defaults to `docs/index.md`).

### `main()`
- Orchestrates the script by reading `home.md`, fetching the top 5 files, generating the markdown content, and writing the result to `index.md`.

## Usage

1. **Folder Setup**: Make sure you have a folder structure with markdown files under `../../docs/` and a `home.md` file located at `../../samplefiles/`.
2. **Run the Script**: Execute the script. It will:
   - Scan the `../../docs/` folder for markdown files (excluding `index.md`).
   - Sort them by modification date.
   - Generate a list of the top 5 files formatted as `[[FileName|Heading]]`.
   - Write the result to `../../docs/index.md`, preceded by the content from `home.md`.

## Example

For instance, if the top 5 files are:

- `myfile1.md` (heading: "Introduction")
- `myfile2.md` (heading: "Installation Guide")
- `myfile3.md` (heading: "FAQ")
- `myfile4.md` (heading: "Getting Started")
- `myfile5.md` (heading: "Release Notes")

The generated `index.md` will contain:

```
# Home Content (from home.md)

# Latest Modified Files

1. [[myfile1|Introduction]]
2. [[myfile2|Installation Guide]]
3. [[myfile3|FAQ]]
4. [[myfile4|Getting Started]]
5. [[myfile5|Release Notes]]
```

## Requirements

- Python 3.x
- UTF-8 encoding support (for reading/writing files)

## Running the Script

To run the script, execute the following command in the terminal:

```bash
python script_name.py
```

This will scan the markdown files and update the `index.md` file with the latest content.
