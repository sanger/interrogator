![Ruby](https://img.shields.io/badge/ruby-%23CC342D.svg?style=for-the-badge&logo=ruby&logoColor=white)

# iSuite-Dashboard

A visualisation tool for Integration Suite test runs.

## Setup

1. Acquire a token for the GitLab API from the GitLab instance you want to use, save the token in a file named `gitlab.token` in the root of the project.
1. Run the server
   ```sh
   bundle exec rerun ruby dashboard/serve.rb
   ```

## Linting

```sh
 bundle exec rubocop -a
```
