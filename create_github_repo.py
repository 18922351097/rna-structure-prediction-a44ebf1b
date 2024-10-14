import os
import requests

def create_github_repo(repo_name='rna-structure-prediction'):
    github_token = os.environ['GITHUB_TOKEN']
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'name': repo_name,
        'description': 'RNA Secondary Structure Prediction and Visualization project',
        'private': False
    }
    response = requests.post('https://api.github.com/user/repos', headers=headers, json=data)

    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully")
        repo_url = response.json()['clone_url']
        print(f"Repository URL: {repo_url}")
        return repo_url
    elif response.status_code == 422:
        print(f"Repository '{repo_name}' already exists. Trying with a different name...")
        return create_github_repo(f"{repo_name}-{os.urandom(4).hex()}")
    else:
        print(f"Failed to create repository. Status code: {response.status_code}")
        print(f"Error message: {response.text}")
        return None

if __name__ == "__main__":
    create_github_repo()
