import os
import zipfile
from pathlib import Path

def unzip_all_files(root_dir="."):
    """Recursively unzip all zip files in a directory."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".zip"):
                zip_path = os.path.join(dirpath, filename)
                extract_dir = os.path.join(dirpath, filename[:-4])
                
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    print(f"Extracted: {zip_path}")
                except Exception as e:
                    print(f"Error extracting {zip_path}: {e}")

if __name__ == "__main__":
    unzip_all_files()