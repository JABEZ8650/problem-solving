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
    """Fetch LeetCode submissions using GraphQL API."""
    url = "https://leetcode.com/graphql"
    headers = {"Content-Type": "application/json"}
    payload = {
        "query": """
        query recentAcSubmissions($username: String!) {
            recentAcSubmissionList(username: $username) {
                title
                timestamp
            }
        }
        """,
        "variables": {"username": LEETCODE_USERNAME}
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"❌ Failed to fetch LeetCode submissions. Status Code: {response.status_code}")
        return []

    data = response.json()
    if "data" not in data or "recentAcSubmissionList" not in data["data"]:
        print("❌ LeetCode API response format changed or no data available.")
        return []

    submissions = []
    for sub in data["data"]["recentAcSubmissionList"]:
        problem_name = sub["title"].replace(" ", "_")
        submissions.append((problem_name, "Python"))  # Defaulting to Python

    return submissions


def fetch_codeforces_submissions():
    """Fetch the latest accepted Codeforces submissions via API."""
    response = requests.get(CODEFORCES_API_URL)
    if response.status_code != 200:
        print(f"❌ Failed to fetch Codeforces submissions. Status Code: {response.status_code}")
        return []

    data = response.json()
    if "result" not in data:
        print("❌ Codeforces API response format changed.")
        return []

    submissions = []

    for sub in data["result"]:
        if sub["verdict"] == "OK":
            problem_name = f"{sub['problem']['contestId']}_{sub['problem']['index']}_{sub['problem']['name'].replace(' ', '_')}"
            language = sub["programmingLanguage"]
            submissions.append((problem_name, language))

    return submissions


def save_submission(folder, problem_name, language, code=""):
    """Save the submission to the correct folder with a structured filename."""
    os.makedirs(folder, exist_ok=True)  # Ensure folder exists

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
    
    # Check for changes before committing
    if repo.is_dirty(untracked_files=True):
        repo.git.add(all=True)
        repo.index.commit(GITHUB_COMMIT_MESSAGE)
        repo.remotes.origin.push()
        print("🚀 Pushed updates to GitHub!")
    else:
        print("✅ No new changes to push.")


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
