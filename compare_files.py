# This script compares two text files containing blocks of text
# and outputs the differences in both console and markdown format.
# It is designed to handle blocks of text that start with a specific header
# and end with a specific footer, allowing for structured comparison of configuration files
# or similar structured text files.

# --- import necessary modules ---
import sys

# --- define constants ---
BLOCK_START = "access-rule"
BLOCK_END = "exit"

def extract_blocks(filename):
    blocks = []
    current_block = []
    rule_header = None
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(BLOCK_START):
                if current_block:
                    blocks.append((rule_header, "".join(current_block)))
                    current_block = []
                rule_header = line.strip()
                current_block.append(line)
            elif line.strip().startswith(BLOCK_END):
                current_block.append(line)
                if rule_header:
                    blocks.append((rule_header, "".join(current_block)))
                current_block = []
                rule_header = None
            elif rule_header:
                current_block.append(line)
    if current_block and rule_header:
        blocks.append((rule_header, "".join(current_block)))
    return blocks

def compare_files(file1, file2):
    blocks1 = extract_blocks(file1)
    blocks2 = extract_blocks(file2)

    dict1 = {header: content for header, content in blocks1}
    dict2 = {header: content for header, content in blocks2}

    # Only consider headers present in both files
    common_headers = set(dict1.keys()).intersection(dict2.keys())
    if not common_headers:
        print("❗ No common blocks found!")
        return

    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    
    # Start comparison
    print(f"Comparing {file1} and {file2}...")
    markdown_lines = [f"# Comparison: {file1} vs {file2}\n"]
    for header in sorted(common_headers):
        if dict1[header] == dict2[header]:
            print(f"Identical block: {header}")
            # Markdown for identical blocks
            markdown_lines.append(f"## {header}\nIdentical block\n")
        else:
            # Strip trailing and leading whitespace for fair comparison
            lines1 = [l.rstrip('\r\n').strip() for l in dict1[header].splitlines()]
            lines2 = [l.rstrip('\r\n').strip() for l in dict2[header].splitlines()]
            set1 = set(lines1)
            set2 = set(lines2)
            only1 = [line for line in lines1 if line not in set2]
            only2 = [line for line in lines2 if line not in set1]
            # Console output with color coding
            print(f"\nDifferences in block: {header}")
            for line in only1:
                print(f"{RED}- {line}{RESET}")
            for line in only2:
                print(f"{GREEN}+ {line}{RESET}")
            if line not in only1 and line not in only2:
                print(f"Follow the white rabbit: 🐇")
            # Markdown for differences
            markdown_lines.append(f"## {header}\n**Differences in block:**\n")
            markdown_lines.append("```diff")
            for line in only1:
                markdown_lines.append(f"- {line}")
            for line in only2:
                markdown_lines.append(f"+ {line}")
            if line not in only1 and line not in only2:
                markdown_lines.append(f"Follow the white rabbit: 🐇")
            markdown_lines.append("```")

    # Write the markdown output to a file
    if not markdown_lines:
        print("❗ No differences found!")
        return
    md_filename = f"comparison_{file1.lstrip('.\\')}_vs_{file2.lstrip('.\\')}.md"
    try:
        with open(md_filename, "w", encoding="utf-8") as md_file:
            md_file.write("\n".join(markdown_lines))
        print(f"\nMarkdown diff saved as: {md_filename}")
    except Exception as e:
        print(f"Error writing markdown file: {e}")

# --- main function to run the script ---

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❗ Please provide two filenames!")
        print("Example: python compare_files.py file1.txt file2.txt")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    compare_files(file1, file2)

# --- end of script ---
# Note: This script assumes that the input files are structured correctly
