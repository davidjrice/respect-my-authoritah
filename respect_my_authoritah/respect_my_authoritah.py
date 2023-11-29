import os
import subprocess
import sys
import uuid
import requests
from tomlkit import parse, dumps

class Authoritah:
    def __init__(self) -> None:
        pass

    def get_current_repo(self) -> str:
        url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).strip().decode('utf-8')
        if url.endswith('.git'):
            url = url[:-4]
        if url.startswith('git@'):
            url = 'https://' + url[4:].replace(':', '/')
        repo = url.split('/')[-2:]
        return '/'.join(repo)

    def respect(self) -> None:
        # Fetch contributors from GitHub API
        # repo = os.getenv('GITHUB_REPOSITORY')
        repo = self.get_current_repo()
        print(repo)

        token = os.getenv('RESPECT_MY_AUTHORITAH_TOKEN')
        headers = {'Authorization': f'token {token}'}
        response = requests.get(f'https://api.github.com/repos/{repo}/contributors', headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch contributors: {response.content}")
            sys.exit(1)
        print(response)

        contributors = [user['login'] for user in response.json()]
        print(contributors)

        # Read and parse pyproject.toml
        with open('pyproject.toml', 'r') as file:
            pyproject = parse(file.read())

        # Update authors list
        pyproject['project']['authors'] = contributors

        # Write back to pyproject.toml
        with open('pyproject.toml', 'w') as file:
            file.write(dumps(pyproject))

        # Create a new branch
        branch_name = f"update-authors-{uuid.uuid4().hex}"
        os.system(f'git checkout -b {branch_name}')

        # Commit and push changes
        os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        os.system('git config --global user.name "GitHub Actions"')
        os.system('git config --global credential.useHttpPath true')

        os.system('git add pyproject.toml')
        os.system('git commit -m "Update authors list"')
        os.system(f'git push https://{token}:x-oauth-basic@github.com/{repo}.git {branch_name}')

        # Create a new pull request
        pr_data = {
            'title': 'Update authors list',
            'head': branch_name,
            'base': 'main',
        }
        response = requests.post(f'https://api.github.com/repos/{repo}/pulls', headers=headers, json=pr_data)
        if response.status_code not in [200, 201]:
            print(f"Failed to create pull request: {response.content}")
            sys.exit(1)
        print(response)

        print("Pull request created successfully")
