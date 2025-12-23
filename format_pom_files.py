#!/usr/bin/env python3
"""
Script to format all descendant pom.xml files in a folder
by replacing tabs with 2 whitespace indents and converting 4-space indentation to 2-space.
"""

import argparse
import os
import re
import sys


def convert_indentation(content, target_spaces=2):
    """
    Format indentation to the target number of spaces.
    Handles:
    1. Tabs -> target_spaces
    2. 4-space indentation -> target_spaces (if consistent 4-space indent is detected)
    """
    lines = content.split("\n")
    
    # Pass 1: Convert Tabs to target_spaces
    # We maintain the list to check for 4-space pattern later
    pass1_lines = []
    for line in lines:
        match = re.match(r"^(\s*)", line)
        if match:
            leading = match.group(1)
            # If tabs exist, convert 1 tab to 1 indentation level (target_spaces)
            if "\t" in leading:
                new_leading = leading.replace("\t", " " * target_spaces)
                line = new_leading + line[len(leading):]
        pass1_lines.append(line)

    # If target is not 2, we don't perform the 4->2 shrinkage logic automatically
    # as the requirement essentially maps 4->2.
    if target_spaces != 2:
        return "\n".join(pass1_lines)

    # Pass 2: Detect if the file (after tab conversion) typically uses 4 spaces
    # Condition: 
    # - Has indented lines
    # - All indented lines are multiples of 4 spaces
    # - No lines with 2 spaces (that are not 4), 6 spaces, etc.
    
    has_indent = False
    is_consistent_4_space = True
    
    for line in pass1_lines:
        match = re.match(r"^( +)", line)
        if match:
            leading_len = len(match.group(1))
            if leading_len > 0:
                has_indent = True
                if leading_len % 4 != 0:
                    # Found a line like 2, 6, 10 spaces... 
                    # This contradicts pure 4-space indentation
                    is_consistent_4_space = False
                    break
    
    # Pass 3: If 4-space indentation is detected, shrink to 2 spaces
    if has_indent and is_consistent_4_space:
        final_lines = []
        for line in pass1_lines:
            match = re.match(r"^( +)(.*)", line)
            if match:
                leading_len = len(match.group(1))
                content_part = match.group(2)
                # Shrink by half (4->2, 8->4)
                new_leading = " " * (leading_len // 2)
                final_lines.append(new_leading + content_part)
            else:
                final_lines.append(line)
        return "\n".join(final_lines)

    return "\n".join(pass1_lines)


def format_pom_file(file_path, spaces_per_tab=2, dry_run=False, verbose=False):
    """
    Format a single pom.xml file by replacing tabs with spaces.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        formatted_content = convert_indentation(original_content, spaces_per_tab)

        # Check if changes are needed
        if original_content == formatted_content:
            if verbose:
                print(f"No changes needed for: {file_path}")
            return False

        if dry_run:
            print(f"Would format: {file_path}")
            return True

        # Write the formatted content back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)

        print(f"Formatted: {file_path}")
        return True
    except OSError as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False


def find_and_format_pom_files(root_dir, spaces_per_tab=2, dry_run=False, verbose=False):
    """
    Recursively find and format all pom.xml files in root_dir.
    """
    formatted_count = 0
    total_files = 0

    for root, dirs, files in os.walk(root_dir):
        # Skip hidden directories (like .git)
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.lower() == "pom.xml":
                file_path = os.path.join(root, file)
                total_files += 1

                if format_pom_file(file_path, spaces_per_tab, dry_run, verbose):
                    formatted_count += 1

    return total_files, formatted_count


def main():
    """
    Main function to parse arguments and run the formatter.
    """
    parser = argparse.ArgumentParser(description="Format pom.xml files: tabs -> 2 spaces, and 4 spaces -> 2 spaces.")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to search for pom.xml files (default: current directory)",
    )
    parser.add_argument("--spaces", type=int, default=2, help="Number of spaces per tab (default: 2)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without actually making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--exclude-dirs",
        nargs="+",
        default=[
            ".git",
            ".svn",
            ".hg",
            "target",
            "node_modules",
            "build",
            ".idea",
            ".vscode",
        ],
        help="Directory to exclude from search",
    )

    args = parser.parse_args()

    # Check if directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Searching for pom.xml files in: {os.path.abspath(args.directory)}")
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
    print(f"Replacing tabs with {args.spaces} spaces")
    print("---")

    total_files, formatted_count = find_and_format_pom_files(args.directory, args.spaces, args.dry_run, args.verbose)

    print("---")
    print(f"Total pom.xml files found: {total_files}")
    if args.dry_run:
        print(f"Files that would be formatted: {formatted_count}")
    else:
        print(f"Files formatted: {formatted_count}")


if __name__ == "__main__":
    main()
