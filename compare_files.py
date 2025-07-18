# This script compares two text files containing blocks of text
# and outputs the differences in both console and markdown format.
# It is designed to handle blocks of text that start with a specific header
# and end with a specific footer, allowing for structured comparison of configuration files
# or similar structured text files.

# --- import necessary modules ---
import sys
import difflib

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
        print("❗ Keine gemeinsamen Blöcke gefunden!")
        return

    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    
    # Start comparison
    print(f"Vergleiche {file1} und {file2}...")
    markdown_lines = [f"# Vergleich: {file1} vs {file2}\n"]
    for header in sorted(common_headers):
        if dict1[header] == dict2[header]:
            print(f"identischer Block: {header}")
            # Markdown for identical blocks
            markdown_lines.append(f"## {header}\nIdentisch\n")
        else:
            lines1 = dict1[header].splitlines()
            lines2 = dict2[header].splitlines()
            diff = list(difflib.ndiff(lines1, lines2))
            # Console output with color coding
            print(f"\nUnterschiede im Block: {header}")
            for line in diff:
                if line.startswith('- '):
                    print(f"{RED}{line}{RESET}")
                elif line.startswith('+ '):
                    print(f"{GREEN}{line}{RESET}")
                elif line.startswith('? '):
                    continue
                else:
                    print(line)
            # Markdown for differences
            markdown_lines.append(f"## {header}\n**Unterschiede im Block:**\n")
            markdown_lines.append("```diff")
            for line in diff:
                if not line.startswith('? '):
                    markdown_lines.append(line)
            markdown_lines.append("```")

    # Write the markdown output to a file
    if not markdown_lines:
        print("❗ Keine Unterschiede gefunden!")
        return
    md_filename = f"vergleich_{file1.lstrip('.\\')}_vs_{file2.lstrip('.\\')}.md"
    try:
        with open(md_filename, "w", encoding="utf-8") as md_file:
            md_file.write("\n".join(markdown_lines))
        print(f"\nMarkdown-Diff gespeichert als: {md_filename}")
    except Exception as e:
        print(f"Fehler beim Schreiben der Markdown-Datei: {e}")

# --- main function to run the script ---

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❗ Bitte zwei Dateinamen angeben!")
        print("Beispiel: python compare_files.py datei1.txt datei2.txt")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    compare_files(file1, file2)

# --- end of script ---
# Note: This script assumes that the input files are structured correctly