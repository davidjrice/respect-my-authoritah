import os
import requests
import toml

class Authoritah:
    def __init__(self) -> None:
        pass

    def respect(self) -> None:
        # Fetch contributors from GitHub API
        repo = os.getenv('GITHUB_REPOSITORY')
        token = os.getenv('GITHUB_TOKEN')
        headers = {'Authorization': f'token {token}'}
        response = requests.get(f'https://api.github.com/repos/{repo}/contributors', headers=headers)
        contributors = [user['login'] for user in response.json()]

        # Read and parse pyproject.toml
        with open('pyproject.toml', 'r') as file:
            pyproject = toml.load(file)

        # Update authors list
        pyproject['tool']['poetry']['authors'] = contributors

        # Write back to pyproject.toml
        with open('pyproject.toml', 'w') as file:
            toml.dump(pyproject, file)

        # Commit and push changes
        os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        os.system('git config --global user.name "GitHub Actions"')
        os.system('git add pyproject.toml')
        os.system('git commit -m "Update authors list"')
        os.system('git push')
