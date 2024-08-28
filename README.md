[![python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=FFD43B)](https://docs.python.org/3.10/)

# iSuite-Dashboard

A visualisation tool for Integration Suite test runs.

## Setup

1. Install Pipenv
1. Install dependencies
   ```sh
    pipenv install --dev
   ```
1. Acquire a token for the GitLab API from the GitLab instance you want to use, save the token in a file named `gitlab.token` in the root of the project.
1. Run the server (flags are optional)
   ```sh
    pipenv run flask --app dashboard/serve run --host=0.0.0.0 --port=5050 --debug
   ```

## Linting

```sh
ruff check --fix **/*.py
djlint dashboard/templates/* --reformat
```
