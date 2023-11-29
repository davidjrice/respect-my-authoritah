import os
import subprocess
import sys
import uuid
import requests
import tomlkit
from jinja2 import Template


class Authoritah:
    def __init__(self) -> None:
        pass

    def get_current_repo(self) -> str:
        url = (
            subprocess.check_output(["git", "config", "--get", "remote.origin.url"])
            .strip()
            .decode("utf-8")
        )
        if url.endswith(".git"):
            url = url[:-4]
        if url.startswith("git@"):
            url = "https://" + url[4:].replace(":", "/")
        repo = url.split("/")[-2:]
        return "/".join(repo)

    def respect(self) -> None:
        # Fetch contributors from GitHub API
        # repo = os.getenv('GITHUB_REPOSITORY')
        repo = self.get_current_repo()
        print(repo)

        token = os.getenv("RESPECT_MY_AUTHORITAH_TOKEN")
        headers = {"Authorization": f"token {token}"}
        response = requests.get(
            f"https://api.github.com/repos/{repo}/contributors", headers=headers
        )
        if response.status_code != 200:
            print(f"Failed to fetch contributors: {response.content}")
            sys.exit(1)
        print(response)

        contributors = [user["login"] for user in response.json()]
        print(contributors)

        contributors_info = []

        for username in contributors:
            response = requests.get(
                f"https://api.github.com/users/{username}", headers=headers
            )
            user_data = response.json()
            name = user_data.get("name", "")
            email = user_data.get("email", "")

            if not email:
                break

            user_info = {
                "name": name,
                "email": email,
            }
            contributors_info.append(user_info)

        print(contributors_info)

        # Read and parse pyproject.toml
        with open("pyproject.toml", "r") as file:
            pyproject = tomlkit.parse(file.read())

        authors_field_exists = "authors" in pyproject["project"]

        # Get current authors list
        current_authors = pyproject["project"].get("authors", [])

        # Convert contributors_info and current_authors to sets for easy comparison
        contributors_info_set = set(tuple(info.items()) for info in contributors_info)
        current_authors_set = set(tuple(author.items()) for author in current_authors)

        # Check if authors list has changed
        if contributors_info_set == current_authors_set:
            print("Authors list has not changed")
            sys.exit(0)

        # Update authors list
        pyproject["project"]["authors"] = list(contributors_info)

        if not authors_field_exists:
            # Add newline after authors field
            print("Authors field already does not exist, adding a newline")
            pyproject["project"].add(tomlkit.nl())

        # Write back to pyproject.toml
        with open("pyproject.toml", "w") as file:
            file.write(tomlkit.dumps(pyproject))

        # Create a new branch
        branch_name = f"update-authors-{uuid.uuid4().hex}"
        os.system(f"git checkout -b {branch_name}")

        # Commit and push changes
        os.system(
            'git config --global user.email "github-actions[bot]@users.noreply.github.com"'
        )
        os.system('git config --global user.name "GitHub Actions"')
        os.system("git config --global credential.useHttpPath true")

        os.system("git add pyproject.toml")
        os.system('git commit -m "Update authors list"')
        os.system(
            f"git push https://{token}:x-oauth-basic@github.com/{repo}.git {branch_name}"
        )

        # Read the markdown PR template
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, "template.md")
        with open(template_path, "r") as file:
            template = Template(file.read())

        # Render the template with the authors list
        body = template.render(authors=contributors_info)

        # Create a new pull request
        pr_data = {
            "title": "chore: update authors",
            "head": branch_name,
            "base": "main",
            "body": body,
        }
        response = requests.post(
            f"https://api.github.com/repos/{repo}/pulls", headers=headers, json=pr_data
        )
        if response.status_code not in [200, 201]:
            print(f"Failed to create pull request: {response.content}")
            sys.exit(1)
        print(response)

        print("Pull request created successfully")
