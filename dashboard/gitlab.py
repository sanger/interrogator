import re
from collections import namedtuple

import requests

GITLAB_URL = "https://gitlab.internal.sanger.ac.uk/"

with open("gitlab.token") as f:
    GRAPHQL_TOKEN = f.read().strip()

FailedTest = namedtuple("FailedTest", ["ref", "comment"])


def query_pipelines():
    with open("dashboard/pipelines.gql") as f:
        headers = {
            "Authorization": f"Bearer {GRAPHQL_TOKEN}",
            "Content-Type": "application/json",
        }
        query = f.read()
        response = requests.post(
            GITLAB_URL + "api/graphql", headers=headers, json={"query": query}
        )

        # collapse edges and nodes
        pipelines = [
            {
                **edge["node"],
                "jobs": [job["node"] for job in edge["node"]["jobs"]["edges"]],
            }
            for edge in response.json()["data"]["project"]["pipelines"]["edges"]
        ]

        return pipelines


def extract_failed_tests(summary):
    """
    Extract the failed tests from the summary.

    Given:
        Failed examples:

        rspec ./spec/limber/scrna_core_spec.rb:140 # Following the high throughput scRNA Core Cell Extraction pipeline scRNA Core entry point 1 - LRC Blood Vac tubes Blood Banking

        Randomized with seed 26337

    Return lines after "Failed examples:" and before "Randomized with seed"
    """
    regex = r"Failed examples:(.*)Randomized with seed"
    match = re.search(regex, summary, re.DOTALL)
    return match.group(1).strip().split("<br/>") if match else []


def failed_tests(pipeline):
    failed_tests = []
    for job in pipeline["jobs"]:
        if job["trace"] and "Failed examples:" in job["trace"]["htmlSummary"]:
            for test in extract_failed_tests(job["trace"]["htmlSummary"]):
                if test:
                    failed_tests.append(FailedTest(*(test.split(" # "))))

    return failed_tests
