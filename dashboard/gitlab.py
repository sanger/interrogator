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
                    failed_tests.append(FailedTest(*(test[6:].split(" # "))))

    return failed_tests


def extract_application_versions(html_summary):
    """
    Extract the application versions from the HTML summary.

    Given:
        1 example, 0 failures, 1 pending<br/><br/>
        Application versions deployed in uat environment:<br/>
          Sequencescape v14.41.0-10509115791-develop@a601903<br/>
          Limber v3.57.0-beta.3@244a226<br/><br/>
        Randomized with seed 26068<br/>

    Return a dictionary of application versions.
    """
    versions = {}
    if "Application versions" in html_summary:
        regex = r"Application versions deployed in \w+ environment:(.*)<br/><br/>"
        match = re.search(regex, html_summary, re.DOTALL)
        if match:
            for line in match.group(1).strip().split("<br/>"):
                if line.startswith("  "):
                    app, version = line.strip().split(" ")
                    versions[app] = version

    return versions


def application_versions(pipeline):
    """Extract the application versions from the pipeline, returning a dictionary."""
    versions = {}
    for job in pipeline["jobs"]:
        html_summary = job["trace"].get("htmlSummary", "") if job["trace"] else ""
        if "Application versions" in html_summary:
            new_versions = extract_application_versions(html_summary)
            for key, new_value in new_versions.items():
                if key in versions and versions[key] != new_value:
                    versions[key] = "version changed during test run"
                else:
                    versions[key] = new_value

    if versions == {}:
        return None

    # convert dictionary to object with attributes sequencescape_version and limber_version
    versions = namedtuple(
        "ApplicationVersions", "sequencescape_version limber_version"
    )(versions.get("Sequencescape"), versions.get("Limber"))
    return versions
