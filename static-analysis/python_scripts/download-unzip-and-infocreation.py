import requests
import os
import csv
import zipfile
import sys
import json

DOWNLOAD_DIR = "./plugins"
RESULTS_DIR = "./results"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

if len(sys.argv) != 3:
    print("python download-and-unzip.py <path_to_plugins_sorted.csv> <num_iteration>")
    sys.exit(1)

csv_download_file = sys.argv[1]
num_iteration = int(sys.argv[2])

print(f"Reading plugins from {csv_download_file} and downloading plugin number {num_iteration}.")

def save_info():
    info_path = os.path.join(RESULTS_DIR, f"{slug}", "info.json")
    try:
        os.makedirs(os.path.dirname(info_path), exist_ok=True)
        with open(info_path, "w") as info_file:
            json.dump(plugin, info_file)
        print(f"Saved plugin info to {info_path}")
    except Exception as e:
        print(f"Error saving plugin info for {slug}: {e}")    

#Encoding to handle BOM
try:
    with open(sys.argv[1], "r", encoding="utf-8-sig") as f:
        plugins = csv.DictReader(f)

        for i, plugin in enumerate(plugins):
            if i != num_iteration:
                continue
            slug = plugin['slug']
            download_link = plugin['download_link']
            print(f"Downloading {slug} from {download_link}")
            try:
                r = requests.get(download_link)
                if r.status_code == 200:
                    zip_path = os.path.join(DOWNLOAD_DIR, f"{slug}.zip")
                    with open(zip_path, "wb") as zip_file:
                        zip_file.write(r.content)
                    print(f"Saved {zip_path}")
                else:
                    print(f"Failed to download {slug}: HTTP {r.status_code}")
            except Exception as e:
                print(f"Error downloading {slug}: {e}")

            #unzip the file
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    extract_path = os.path.join(DOWNLOAD_DIR)
                    zip_ref.extractall(extract_path)
                    print(f"Extracted {zip_path} to {extract_path}")
            except Exception as e:
                print(f"Error extracting {zip_path}: {e}")

            #delete zip
            try:
                os.remove(zip_path)
                print(f"Deleted {zip_path}")
            except Exception as e:
                print(f"Error deleting {zip_path}: {e}")

            #save info.json
            save_info()
except Exception as e:
    save_info()
    print(f"Error handling plugin {e}") 
