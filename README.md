![Ruby](https://img.shields.io/badge/ruby-%23CC342D.svg?style=for-the-badge&logo=ruby&logoColor=white)

# Interrogator

A visualisation tool for Integration Suite test runs.

![Screenshot](docs/screenshot.png)

## Setup

1. Install dependencies
   ```sh
   bundle install
   ```
1. Acquire a [personal access token](https://gitlab.internal.sanger.ac.uk/-/user_settings/personal_access_tokens) for the GitLab API from the GitLab instance you want to use. Set the token name to `{username}-interrogator`, expiration date to a year's time and scope to `read_api`. Save the token in a file named `gitlab.token` in the root of the project.
1. Run the server
   ```sh
   bundle exec rerun ruby app.rb
   ```
1. Access the interface at http://localhost:4567

## Linting

```sh
bundle exec rubocop -a
bundle exec erblint --lint-all -a
```
