#!/usr/bin/env python3
"""
Script to format all descendant pom.xml files in a folder
by replacing tabs with 2 whitespace indents
"""

import os
import re
import argparse
import sys


def replace_tabs_with_spaces(content, spaces_per_tab=2):
    """
    Replace tabs with specified number of spaces in content.
    Handles mixed indentation properly.
    """
    lines = content.split("\n")
    result_lines = []

    for line in lines:
        # Find leading whitespaces
        leading_whitespace = re.match(r"^(\s*)", line).group(1)

        if "\t" in leading_whitespace:
            # Count tabs and spaces in leading whitespace
            tab_count = leading_whitespace.count("\t")
            space_count = len(leading_whitespace) - tab_count

            # Convert tabs to spaces
            new_leading_whitespace = ' ' * (tab_count * spaces_per_tab + space_count)

            # Replace the leading whitespace
            line = new_leading_whitespace + line[len(leading_whitespace):]

        # Also replace any tabs in the rest of the line (though unusual in XML)
        line = line.replace('\t', ' ' * spaces_per_tab)
        result_lines.append(line)

    return '\n'.join(result_lines)


def format_pom_file(file_path, spaces_per_tab=2, dry_run=False, verbose=False):
    """
    Format a single pom.xml file by replacing tabs with spaces.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        formatted_content = replace_tabs_with_spaces(original_content, spaces_per_tab)

        # Check if changes are needed
        if original_content == formatted_content:
            if verbose:
                print(f"No changes needed for: {file_path}")
            return False

        if dry_run:
            print(f"Would format: {file_path}")
            return True

        # Write the formatted content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

        print(f"Formatted: {file_path}")
        return True
    except Exception as e:
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
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.lower() == 'pom.xml':
                file_path = os.path.join(root, file)
                total_files += 1

                if format_pom_file(file_path, spaces_per_tab, dry_run, verbose):
                    formatted_count += 1

    return total_files, formatted_count


def main():
    parser = argparse.ArgumentParser(
        description="Format all descendant pom.xml files by replacing tabs with 2 spaces."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to search for pom.xml files (default: current directory)"
    )
    parser.add_argument(
        "--spaces",
        type=int,
        default=2,
        help="Number of spaces per tab (default: 2)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without actually making changes"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--exclude-dirs",
        nargs="+",
        default=[".git", ".svn", ".hg", "target", "node_modules", "build", ".idea", ".vscode"],
        help="Directory to exclude from search"
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

    total_files, formatted_count = find_and_format_pom_files(
        args.directory,
        args.spaces,
        args.dry_run,
        args.verbose
    )

    print("---")
    print(f"Total pom.xml files found: {total_files}")
    if args.dry_run:
        print(f"Files that would be formatted: {formatted_count}")
    else:
        print(f"Files formatted: {formatted_count}")


if __name__ == "__main__":
    main()
