import os
import requests
import json
import time
from bs4 import BeautifulSoup
from git import Repo

# GitHub Configuration
GITHUB_REPO_PATH = "/home/hmmm/problem-solving" 
GITHUB_COMMIT_MESSAGE = "Auto-update problem solutions"
GITHUB_BRANCH = "main"

# LeetCode Configuration
LEETCODE_USERNAME = "eyumuhaba"  

# Codeforces Configuration
CODEFORCES_HANDLE = "Jabez"  
CODEFORCES_API_URL = f"https://codeforces.com/api/user.status?handle={CODEFORCES_HANDLE}&from=1&count=10"


def fetch_leetcode_submissions():
    """Scrape the latest accepted LeetCode submissions."""
    url = f"https://leetcode.com/{LEETCODE_USERNAME}/submissions/"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ Failed to fetch LeetCode submissions.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    submissions = []

    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        status = cols[2].text.strip()
        if status != "Accepted":
            continue

        problem_name = cols[1].text.strip().replace(" ", "_")
        language = cols[3].text.strip()

        submissions.append((problem_name, language))

    return submissions


def fetch_codeforces_submissions():
    """Fetch the latest accepted Codeforces submissions via API."""
    response = requests.get(CODEFORCES_API_URL)
    if response.status_code != 200:
        print("❌ Failed to fetch Codeforces submissions.")
        return []

    data = response.json()
    submissions = []

    for sub in data["result"]:
        if sub["verdict"] == "OK":
            problem_name = f"{sub['problem']['contestId']}_{sub['problem']['index']}_{sub['problem']['name'].replace(' ', '_')}"
            language = sub["programmingLanguage"]
            submissions.append((problem_name, language))

    return submissions


def save_submission(folder, problem_name, language, code=""):
    """Save the submission to the correct folder with a structured filename."""
    ext_map = {
        "Python": ".py",
        "C++": ".cpp",
        "Java": ".java",
        "JavaScript": ".js"
    }

    ext = ext_map.get(language.split()[0], ".txt")  # Default to .txt if unknown
    filename = f"{folder}/{problem_name}{ext}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code if code else f"# Solution for {problem_name}")

    print(f"✅ Saved {filename}")


def commit_and_push():
    """Automatically commit and push the new submissions."""
    repo = Repo(GITHUB_REPO_PATH)
    repo.git.add(all=True)
    repo.index.commit(GITHUB_COMMIT_MESSAGE)
    repo.remotes.origin.push()
    print("🚀 Pushed updates to GitHub!")


def main():
    """Main function to fetch, save, and push solutions."""
    print("🔄 Fetching LeetCode submissions...")
    leetcode_solutions = fetch_leetcode_submissions()
    for name, lang in leetcode_solutions:
        save_submission("leetcode", name, lang)

    print("🔄 Fetching Codeforces submissions...")
    codeforces_solutions = fetch_codeforces_submissions()
    for name, lang in codeforces_solutions:
        save_submission("codeforces", name, lang)

    commit_and_push()


if __name__ == "__main__":
    main()
