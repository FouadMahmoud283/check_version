import requests
from bs4 import BeautifulSoup
import os

# URL of the npm page for the React package
URL = "https://www.npmjs.com/package/express?activeTab=versions"

# File to store the last checked version
VERSION_FILE = "last_version.txt"

def fetch_latest_version():
    """Fetch the latest version of React from the npm page."""
    response = requests.get(URL)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing the 'Current Tags' section
    current_tags_table = soup.find("table", {"class": "cab9c622"})
    if not current_tags_table:
        raise Exception("Could not find the 'Current Tags' table on the page.")

    # Extract the latest version from the first row of the table
    latest_version_tag = current_tags_table.find("a")  # First <a> tag in the table
    if not latest_version_tag:
        raise Exception("Could not find the latest version in the 'Current Tags' table.")

    latest_version = latest_version_tag.text.strip()
    return latest_version

def read_last_version():
    """Read the last checked version from the file."""
    if not os.path.exists(VERSION_FILE):
        return None
    with open(VERSION_FILE, "r") as file:
        return file.read().strip()

def save_last_version(version):
    """Save the latest version to the file."""
    with open(VERSION_FILE, "w") as file:
        file.write(version)

def main():
    print("Checking for updates...")
    try:
        latest_version = fetch_latest_version()
        print(f"Latest version found: {latest_version}")

        last_version = read_last_version()
        if last_version is None:
            print("No previous version found. Saving the current version.")
            save_last_version(latest_version)
        elif latest_version != last_version:
            print(f"New version detected! Latest: {latest_version}, Previous: {last_version}")
            # Notify or act based on the new version
            save_last_version(latest_version)
        else:
            print(f"No updates. Latest version ({latest_version}) is the same as the last checked version.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()