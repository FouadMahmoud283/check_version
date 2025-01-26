import requests
from bs4 import BeautifulSoup
import os

# URL of the npm page for the package
URL = "https://www.npmjs.com/package/express?activeTab=versions"
VERSION_FILE = "last_version.txt"
# Hardcoded Express repository URL
REPO_URL = "https://github.com/expressjs/express"

def fetch_latest_version():
    """Fetch the latest version of Express from the npm page."""
    response = requests.get(URL)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Original table detection using class name
    current_tags_table = soup.find("table", {"class": "cab9c622"})
    if not current_tags_table:
        raise Exception("Could not find the 'Current Tags' table on the page.")

    # Extract latest version from first link in table
    latest_version_tag = current_tags_table.find("a")
    if not latest_version_tag:
        raise Exception("Latest version not found in table.")
    
    return latest_version_tag.text.strip()

def parse_github_repo_url():
    """Parse owner and repo from hardcoded URL"""
    parts = REPO_URL.rstrip('/').split('/')
    return parts[-2], parts[-1]  # Returns ('expressjs', 'express')

def get_release_notes(version):
    """Fetch release notes from GitHub using hardcoded repo"""
    owner, repo = parse_github_repo_url()
    tags_to_try = [f"v{version}", version]
    
    for tag in tags_to_try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
        response = requests.get(
            api_url,
            headers={'Accept': 'application/vnd.github.v3+json'}
        )
        if response.status_code == 200:
            return response.json().get('body', 'No release notes available')
        elif response.status_code == 404:
            continue
        else:
            response.raise_for_status()
    
    return f"Release notes not found. Check {REPO_URL}/releases"

def read_last_version():
    """Read the last checked version from file."""
    if not os.path.exists(VERSION_FILE):
        return None
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()

def save_last_version(version):
    """Save the latest version to file."""
    with open(VERSION_FILE, "w") as f:
        f.write(version)

def main():
    print("Checking for Express updates...")
    try:
        latest_version = fetch_latest_version()
        print(f"Latest version found: {latest_version}")

        last_version = read_last_version()
        if last_version is None:
            print("Initial version saved:", latest_version)
            save_last_version(latest_version)
        elif latest_version != last_version:
            print(f"New version detected! {last_version} → {latest_version}")
            try:
                notes = get_release_notes(latest_version)
                print(f"\nChanges in {latest_version}:\n{notes}")
            except Exception as e:
                print(f"\nCouldn't fetch details: {e}")
                print(f"Manual check: {REPO_URL}/releases")
            save_last_version(latest_version)
        else:
            print("No updates - same version as last check")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
