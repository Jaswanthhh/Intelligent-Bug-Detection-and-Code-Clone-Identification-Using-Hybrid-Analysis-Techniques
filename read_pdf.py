from pypdf import PdfReader
import sys
import os

filename = "plan.pdf"
if len(sys.argv) > 1:
    filename = sys.argv[1]

output_filename = filename + ".txt"

try:
    reader = PdfReader(filename)
    print(f"Reading {filename}...")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(f"Number of pages: {len(reader.pages)}\n")
        for i, page in enumerate(reader.pages):
            f.write(f"--- Page {i+1} ---\n")
            text = page.extract_text()
            f.write(text + "\n")
    print(f"Successfully wrote to {output_filename}")
except Exception as e:
    print(f"Error reading PDF: {e}")
