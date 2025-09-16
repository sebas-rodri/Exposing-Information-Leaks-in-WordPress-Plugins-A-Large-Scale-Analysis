import csv
import requests

BASE_URL = "https://api.wordpress.org/plugins/info/1.2/?action=query_plugins&request[per_page]=250&request[page]={}"
NUM_PLUGINS=10000


def fetch_plugins(page):
    response = requests.get(BASE_URL.format(page))
    if response.status_code == 200:
        return response.json().get("plugins", [])
    return []

if __name__ == "__main__":
    all_plugins = []
    res = requests.get(BASE_URL.format(0))
    num_pages = res.json().get("info").get("pages")
    for page in range(1, num_pages + 1): 
        plugins = fetch_plugins(page)
        all_plugins.extend(plugins)

    sorted_plugins = sorted(all_plugins, key=lambda x: x.get("downloaded", 0), reverse=True)

  
    with open("plugins_sorted.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name", "Downloads", "Active Installs", "slug", "version", "download_link"])
        for index, plugin in enumerate(sorted_plugins):
            if index == NUM_PLUGINS:
                break
            writer.writerow([plugin.get("name"), plugin.get("downloaded", 0), plugin.get("active_installs", 0), plugin.get("slug"), plugin.get("version"), plugin.get("download_link")])
        