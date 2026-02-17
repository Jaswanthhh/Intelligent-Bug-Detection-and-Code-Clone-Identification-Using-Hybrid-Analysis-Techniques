import os
import argparse
from datetime import datetime

def generate_review_bundle(folders, output_file="code_review_bundle.md", extensions=None):
    """
    Aggregates code from specified folders into a single Markdown file.
    """
    if extensions is None:
        extensions = ['.py', '.java', '.js', '.cpp', '.h', '.c']

    print(f"[*] Generating code review bundle...")
    print(f"[*] Target folders: {folders}")
    print(f"[*] Output file: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as out:
        # Header
        out.write(f"# Code Review Bundle\n\n")
        out.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        out.write(f"**Included Folders:**\n")
        for f in folders:
            out.write(f"- `{f}`\n")
        out.write("\n---\n\n")

        # Table of Contents
        out.write("## Table of Contents\n\n")
        file_list = []
        for folder in folders:
            if not os.path.exists(folder):
                print(f"[!] Warning: Folder not found: {folder}")
                continue
            
            for root, _, files in os.walk(folder):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in extensions:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, start=os.getcwd())
                        file_list.append((rel_path, full_path, ext))
        
        for rel_path, _, _ in file_list:
            anchor = rel_path.replace('\\', '-').replace('/', '-').replace('.', '').replace(' ', '-').lower()
            out.write(f"- [{rel_path}](#{anchor})\n")
        
        out.write("\n---\n\n")

        # File Contents
        for rel_path, full_path, ext in file_list:
            print(f"  -> Processing {rel_path}")
            
            # Create anchor
            anchor = rel_path.replace('\\', '-').replace('/', '-').replace('.', '').replace(' ', '-').lower()
            
            out.write(f"## {rel_path} <a name=\"{anchor}\"></a>\n\n")
            out.write(f"**Path:** `{full_path}`\n\n")
            
            lang_map = {
                '.py': 'python',
                '.java': 'java',
                '.js': 'javascript',
                '.cpp': 'cpp',
                '.c': 'c',
                '.h': 'cpp'
            }
            lang = lang_map.get(ext, '')
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                out.write(f"```{lang}\n")
                out.write(content)
                out.write(f"\n```\n\n")
                out.write("---\n\n")
            except Exception as e:
                out.write(f"> [!WARNING]\n> Could not read file: {e}\n\n")

    print(f"[*] Done! Saved to {output_file}")

if __name__ == "__main__":
    # Default folders requested by user
    default_folders = [
        "dynamic_testing",
        "samples",
        "semantic_analysis",
        "static_analysis"
    ]
    
    # Adjust paths to be relative to where the script is likely run (project root)
    # Assuming script is placed in project root
    
    parser = argparse.ArgumentParser(description="Generate a code review bundle.")
    parser.add_argument("--folders", nargs="+", default=default_folders, help="List of folders to include")
    parser.add_argument("--output", default="code_review_bundle.md", help="Output markdown file")
    
    args = parser.parse_args()
    
    generate_review_bundle(args.folders, args.output)
