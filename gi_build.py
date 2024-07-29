#!/usr/bin/env python3
"""
gi_build.py

This script generates a .gitignore file based on a list of templates and
included files. It reads the gitignore/gitignore configuration file, processes
the included templates, and writes the combined .gitignore file. If a
.gitignore file already exists, it creates a backup with a timestamp.

Usage:
    Run this script directly to generate the .gitignore file:
    $ ./gi_build.py

License:
    This project is licensed under the MIT License
    https://opensource.org/licenses/MIT
"""

import os
import shutil
from datetime import datetime


def build_gitignore():
    """Build a .gitignore file based on the gitignore list and included
    templates.

    This function reads the gitignore list file, processes the included
    templates, and writes the combined .gitignore file. If a .gitignore file
    already exists, it creates a backup with a timestamp.

    Example:
        To generate the .gitignore file, simply run the script:
        $ ./gi_build.py
    """
    # Get the current working directory
    base_dir = os.getcwd()
    # Get the script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Path to the gitignore list file
    gitignore_list_path = os.path.join(script_dir, "gitignore", "gitignore")
    # Path to the output .gitignore file
    output_gitignore_path = os.path.join(base_dir, ".gitignore")

    # Header for the generated .gitignore file
    header = """\
##############################################################################
# This is a klingon_templates generated .gitignore file DO NOT EDIT DIRECTLY
#
# Usage: This file is generated by the gi_build.py script which pulls config
# from the gitignore/** directories and the project.gitignore file in the root
# of the repo.
#
# Project/user specific config can be put into the project.gitignore file
# which can be found in the root of the repo
#
# License: This project is licensed under the MIT License
#          https://opensource.org/licenses/MIT
##############################################################################
"""
    with open(gitignore_list_path, "r") as f:
        lines = f.readlines()

    included_files = []  # List to store included files and their comments
    current_comment = []  # List to store current comments
    for line in lines:
        stripped_line = line.strip()  # Remove leading and trailing whitespace
        if not stripped_line.startswith("#"):
            if stripped_line.startswith("!"):
                # If the line starts with '!' (include directive), add the file
                # and comments to the list
                included_files.append((line[1:], current_comment))
                # Reset current comments after including a file
                current_comment = []
            else:
                # Reset current comments if the line is not a comment or
                # include directive
                current_comment = []

    # If a .gitignore file already exists, create a backup with a timestamp
    if os.path.exists(output_gitignore_path):
        # Generate a timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # Backup file path
        backup_gitignore_path = f"{output_gitignore_path}-{timestamp}"
        # Move the existing .gitignore to the backup path
        shutil.move(output_gitignore_path, backup_gitignore_path)

    # Write the new .gitignore file with the header
    with open(output_gitignore_path, "w") as out_f:
        # Write the header to the .gitignore file
        out_f.write(header + "\n\n")

        for file_path, comments in included_files:
            # Get the full path of the included file
            full_path = os.path.join(base_dir, file_path.strip())
            if os.path.exists(full_path):
                # If the included file exists, read its content and write to
                # the .gitignore file
                out_f.write(f"## {file_path.strip()} start\n")
                with open(full_path, "r") as in_f:
                    in_header = False
                    for line in in_f:
                        if line.startswith("#" * 79):
                            in_header = not in_header
                        elif not in_header:
                            out_f.write(line)
                out_f.write(f"## {file_path.strip()} end\n\n")
            for comment in comments:
                # Write each comment to the .gitignore file
                out_f.write(comment)


if __name__ == "__main__":
    # Call the build_gitignore function if the script is executed directly
    build_gitignore()
