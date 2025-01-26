import requests
from bs4 import BeautifulSoup
import os

# URL of the npm page for the package
URL = "https://www.npmjs.com/package/express?activeTab=versions"
VERSION_FILE = "last_version.txt"

def fetch_package_info():
    """Fetch the latest version and repository URL from the npm page."""
    response = requests.get(URL)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # REVERTED: Use your original class name to find the versions table
    current_tags_table = soup.find("table", {"class": "cab9c622"})
    if not current_tags_table:
        raise Exception("Could not find the 'Current Tags' table on the page.")

    # Extract latest version (your original logic)
    latest_version_tag = current_tags_table.find("a")
    if not latest_version_tag:
        raise Exception("Latest version not found.")
    latest_version = latest_version_tag.text.strip()

    # Extract repository URL (keep this new addition)
    repo_link = soup.find("a", {"data-testid": "sidebar__repository"})
    if not repo_link:
        raise Exception("Repository link not found.")
        repo_url = "https://github.com/expressjs/express"

    return latest_version, repo_url

def parse_github_repo_url(repo_url):
    """Extract owner and repo name from GitHub URL."""
    repo_url = repo_url.rstrip('/').replace('.git', '')
    parts = repo_url.split('/')
    if len(parts) < 5 or parts[2] != 'github.com':
        raise ValueError(f"Invalid GitHub URL: {repo_url}")
    return parts[-2], parts[-1]

def get_release_notes(owner, repo, version):
    """Fetch release notes from GitHub API."""
    tags = [version, f"v{version}"]
    for tag in tags:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
        response = requests.get(api_url, headers={'Accept': 'application/vnd.github.v3+json'})
        if response.status_code == 200:
            return response.json().get('body', 'No release notes provided.')
        elif response.status_code != 404:
            response.raise_for_status()
    return "Release notes not found."

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
    print("Checking for updates...")
    try:
        latest_version, repo_url = fetch_package_info()
        print(f"Latest version found: {latest_version}")

        last_version = read_last_version()
        if last_version is None:
            print("Saving initial version.")
            save_last_version(latest_version)
        elif latest_version != last_version:
            print(f"New version: {latest_version} (old: {last_version})")
            try:
                owner, repo = parse_github_repo_url(repo_url)
                notes = get_release_notes(owner, repo, latest_version)
                print(f"Changes in {latest_version}:\n{notes}")
            except Exception as e:
                print(f"Couldn't fetch changes: {e}")
            save_last_version(latest_version)
        else:
            print("No updates.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
