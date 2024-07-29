#!/usr/bin/env python3

"""
This script syncs .gitignore files and submodules for a project. It ensures
that the project-specific .gitignore file exists, reads and writes .gitignore
files, and syncs submodules. The script can be run with various command-line
arguments to control its behavior.

Arguments:
    --log_file: Path to log file.
    --dry_run: Perform a dry run.
    --verbose: Enable verbose output.
    --debug: Enable debug output.
    --force: Force sync.
    --no_sync: Do not sync submodules.
    --no_pull: Do not pull latest changes.
    --no_submodule_sync: Do not sync submodules.
    --no_gitignore_sync: Do not sync gitignore file.
    --no_gitignore_sort: Do not sort gitignore sections.
    --no_gitignore_remove: Do not remove missing gitignore files.
    --no_gitignore_add: Do not add new gitignore files.
    --no_gitignore_section_sort: Do not sort gitignore sections.
    --no_gitignore_section_remove: Do not remove missing gitignore sections.
    --no_gitignore_section_add: Do not add new gitignore sections.
    --no_gitignore_section_comment: Do not comment out missing gitignore
    sections.
    --no_gitignore_section_uncomment: Do not uncomment existing gitignore
    sections.
    --no_gitignore_section_sync: Do not sync gitignore sections.

Examples:
    Sync gitignore files and submodules with verbose output:
        python gi_sync.py --verbose

    Perform a dry run without syncing submodules:
        python gi_sync.py --dry_run --no_submodule_sync

    Force sync and enable debug output:
        python gi_sync.py --force --debug
"""

import os
import re
import subprocess
import argparse
import logging

# Regex patterns for section start and end
start_section = r"^## \w+ ignores( \(uncomment as needed\))?$"
end_section = r"^## end gitignore$"


def ensure_running_from_repo_root():
    """
    Ensure the script runs from the directory it lives in.
    Changes the current working directory to the script's directory.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)


def run_git_command(command):
    """
    Run a git command and return its output.

    Args:
        command (str): The git command to run.

    Returns:
        str: The output of the git command.
    """
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        logging.error(f"Git command failed: {command}\n{result.stderr}")
    return result.stdout


def sync_submodules():
    """
    Sync submodules by initializing and updating them recursively.
    """
    run_git_command("git submodule update --init --recursive")


def git_pull():
    """
    Pull the latest changes from the remote repository.
    """
    run_git_command("git pull")


def read_gitignore(file_path):
    """
    Read the contents of a .gitignore file.

    Args:
        file_path (str): The path to the .gitignore file.

    Returns:
        list: A list of lines from the .gitignore file.
    """
    with open(file_path, "r") as file:
        return file.readlines()


def write_gitignore(file_path, lines):
    """
    Write lines to a .gitignore file.

    Args:
        file_path (str): The path to the .gitignore file.
        lines (list): A list of lines to write to the file.
    """
    with open(file_path, "w") as file:
        file.writelines(lines)


def get_gitignore_files(directory, section_files):
    """
    Get all .gitignore files in a directory and classify new ones.

    Args:
        directory (str): The directory to search for .gitignore files.
        section_files (dict): A dictionary of section files.

    Returns:
        list: A list of .gitignore files and their classifications.
    """
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".gitignore")
    ]
    new_files = []
    for file in files:
        if not any(
            file.startswith(prefix) for prefix in section_files.values()
        ):
            classification = input(
                f"Classify the new gitignore file '{file}': "
            )
            new_files.append((file, classification))
    return files + new_files


def ensure_project_gitignore_exists():
    """
    Ensure the project-specific .gitignore file exists.
    Creates the file with a header if it does not exist.
    """
    project_gitignore_path = "project.gitignore"
    if not os.path.exists(project_gitignore_path):
        with open(project_gitignore_path, "w") as file:
            file.write(
                "# This is your project-specific .gitignore file.\n"
                "# Add any project-specific ignore rules here.\n"
                "# This file will be included in the main .gitignore file.\n\n"
                "# Project-specific gitignore rules\n\n"
                "# Don't add aider configs, logs, caches etc\n"
                ".aider*\n"
            )


def sync_gitignore(gitignore_path):
    """
    Sync the main .gitignore file with project-specific and template .gitignore
    files.

    Args:
        gitignore_path (str): The path to the main .gitignore file.
    """
    ensure_project_gitignore_exists()
    lines = read_gitignore(gitignore_path)
    new_lines = []
    section_files = {}
    section_files.update(
        {
            "core": get_gitignore_files(
                "gitignore/klingon_templates/core", section_files
            ),
            "ide": get_gitignore_files(
                "gitignore/klingon_templates/ide", section_files
            ),
            "shell": get_gitignore_files(
                "gitignore/klingon_templates/shell", section_files
            ),
            "language": get_gitignore_files(
                "gitignore/klingon_templates/languages", section_files
            ),
            "github": get_gitignore_files(
                "gitignore/github_templates", section_files
            ),
            "github global": get_gitignore_files(
                "gitignore/github_templates/global", section_files
            ),
            "github community": get_gitignore_files(
                "gitignore/github_templates/community", section_files
            ),
        }
    )

    in_section = False
    section_lines = []
    in_project_ignores = False

    for line in lines:
        if "## project ignores" in line:
            in_project_ignores = True
            new_lines.append(line)
        elif "## end gitignore" in line and in_project_ignores:
            in_project_ignores = False
            new_lines.append(line)
        elif in_project_ignores:
            new_lines.append(line)
        elif re.match(start_section, line):
            in_section = True
            section_lines = []
            new_lines.append(line)
        elif re.match(end_section, line):
            in_section = False
            section_lines.sort(key=lambda x: x.lstrip("#").strip())
            new_lines.extend(section_lines)
            new_lines.append(line)
        elif in_section:
            section_lines.append(line)
        else:
            new_lines.append(line)

    for section, files in section_files.items():
        for file in files:
            if isinstance(file, tuple):
                file, classification = file
                section_files[classification].append(file)
            file_line = f"!{file}\n"
            if file_line not in section_lines:
                section_lines.append(file_line)

    write_gitignore(gitignore_path, new_lines)


def main():
    """
    Main function to parse arguments and run the script.
    """
    parser = argparse.ArgumentParser(
        description="Sync gitignore files and submodules."
    )
    parser.add_argument("--log_file", type=str, help="Path to log file")
    parser.add_argument(
        "--dry_run", action="store_true", help="Perform a dry run"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug output"
    )
    parser.add_argument("--force", action="store_true", help="Force sync")
    parser.add_argument(
        "--no_sync", action="store_true", help="Do not sync submodules"
    )
    parser.add_argument(
        "--no_pull", action="store_true", help="Do not pull latest changes"
    )
    parser.add_argument(
        "--no_submodule_sync",
        action="store_true",
        help="Do not sync submodules",
    )
    parser.add_argument(
        "--no_gitignore_sync",
        action="store_true",
        help="Do not sync gitignore file",
    )
    parser.add_argument(
        "--no_gitignore_sort",
        action="store_true",
        help="Do not sort gitignore sections",
    )
    parser.add_argument(
        "--no_gitignore_remove",
        action="store_true",
        help="Do not remove missing gitignore files",
    )
    parser.add_argument(
        "--no_gitignore_add",
        action="store_true",
        help="Do not add new gitignore files",
    )
    parser.add_argument(
        "--no_gitignore_section_sort",
        action="store_true",
        help="Do not sort gitignore sections",
    )
    parser.add_argument(
        "--no_gitignore_section_remove",
        action="store_true",
        help="Do not remove missing gitignore sections",
    )
    parser.add_argument(
        "--no_gitignore_section_add",
        action="store_true",
        help="Do not add new gitignore sections",
    )
    parser.add_argument(
        "--no_gitignore_section_comment",
        action="store_true",
        help="Do not comment out missing gitignore sections",
    )
    parser.add_argument(
        "--no_gitignore_section_uncomment",
        action="store_true",
        help="Do not uncomment existing gitignore sections",
    )
    parser.add_argument(
        "--no_gitignore_section_sync",
        action="store_true",
        help="Do not sync gitignore sections",
    )
    args = parser.parse_args()

    if args.log_file:
        logging.basicConfig(filename=args.log_file, level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    ensure_running_from_repo_root()

    if not args.no_pull:
        git_pull()

    if not args.no_submodule_sync:
        sync_submodules()

    if not args.no_gitignore_sync:
        sync_gitignore("gitignore/gitignore")


if __name__ == "__main__":
    main()
