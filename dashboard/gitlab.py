import re
from collections import namedtuple
from string import Template

import requests

GITLAB_URL = "https://gitlab.internal.sanger.ac.uk/"

with open("gitlab.token") as f:
    GRAPHQL_TOKEN = f.read().strip()

FailedTest = namedtuple("FailedTest", ["ref", "comment"])


def query_pipelines(first=20, source=None, status=None):
    with open("dashboard/pipelines.gql") as f:
        template = Template(f.read())
        pipelines_filter = f"first: {first}"
        if source and source != "all":
            pipelines_filter += f', source: "{source}"'
        if status and status != "all":
            pipelines_filter += f", status: {status.upper()}"
        query = template.substitute(pipelines_filter=pipelines_filter)

        headers = {
            "Authorization": f"Bearer {GRAPHQL_TOKEN}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            GITLAB_URL + "api/graphql", headers=headers, json={"query": query}
        )

        # collapse edges and nodes
        try:
            pipelines = [
                {
                    **edge["node"],
                    "jobs": [job["node"] for job in edge["node"]["jobs"]["edges"]],
                }
                for edge in response.json()["data"]["project"]["pipelines"]["edges"]
            ]
        except KeyError:
            # no pipelines found
            pipelines = []

        return pipelines


def is_lint(pipeline):
    """Given a pipeline, return True if it is a lint pipeline."""
    for job in pipeline["jobs"]:
        if job["name"] == "job_lint":
            return True
    return False


def pipeline_build_status(pipeline):
    """Given a pipeline, report the status of the build."""
    for job in pipeline["jobs"]:
        if job["name"] == "job_build":
            return job["status"]
    return "No build"


def pipeline_cleanup_status(pipeline):
    """Given a pipeline, report the status of the cleanup job."""
    for job in pipeline["jobs"]:
        if job["name"] == "job_cleanup":
            return job["status"]
    return "No cleanup"


def extract_failed_tests(summary):
    """
    Extract the failed tests from the summary.

    Given:
        Failed examples:
        rspec ./spec/limber/bespoke_pcr_pipeline_spec.rb:31 # Following the Bespoke PCR pipeline 96 well
        rspec ./spec/limber/bespoke_chromium_3pv3_pipeline_spec.rb:38 # Following the Bespoke Chromium Aggregation and 3pv3 pipelines 96 well
        Randomized with seed 59715

    Return lines that start with "rspec ./" and end with "<".
    """
    regex = r"(<br\/>rspec \.\/[^<]+)"
    matches = re.findall(regex, summary, re.DOTALL)
    return "".join(matches).split("<br/>") if matches else []


def failed_tests(pipeline):
    failed_tests = []
    for job in pipeline["jobs"]:
        if job["trace"] and "Failed examples:" in job["trace"]["htmlSummary"]:
            for test in extract_failed_tests(job["trace"]["htmlSummary"]):
                if test:
                    failed_tests.append(FailedTest(*(test[6:].split(" # "))))

    return failed_tests


def pipeline_status(pipeline):
    """Given a pipeline, report the status of the pipeline taking the job stages into account."""
    if is_lint(pipeline):
        return f"lint {pipeline['status']}"
    if pipeline["status"].lower() == "failed":
        if pipeline_build_status(pipeline).lower() == "failed":
            return "build failed"
        elif any(failed_tests(pipeline)):
            n = len(failed_tests(pipeline))
            return f"tests failed ({n})"
        elif pipeline_cleanup_status(pipeline).lower() == "failed":
            return "cleanup failed"

    return pipeline["status"]


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

    # add keys for templates
    versions["sequencescape_version"] = versions.get("Sequencescape")
    versions["limber_version"] = versions.get("Limber")

    return versions
