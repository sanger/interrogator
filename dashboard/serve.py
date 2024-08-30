from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import db
import gitlab
import requests
from applications import fetch_version
from flask import Flask, render_template, request

UNKNOWN_VERSION = "&lt;unknown&gt;"

app = Flask(__name__)
app.config.from_mapping(
    DATABASE=Path(app.root_path) / "dashboard.sqlite",
)
db.init_app(app)


@app.route("/")
def index():
    filters = request.args  # get the query string parameters as the filters
    try:
        pipelines = gitlab.query_pipelines(**filters)
        for pipeline in pipelines:
            # extract the number from the id gid://gitlab/Ci::Pipeline/286655
            pipeline["id"] = pipeline["id"].split("/")[-1]
            pipeline["commit_abbr"] = pipeline["commitPath"].split("/")[-1][:6]
            pipeline["int_suite_version"] = (
                f"{pipeline['ref']}@{pipeline['commit_abbr']}"
            )
            pipeline["overall_status"] = gitlab.pipeline_status(pipeline)
            pipeline["is_tested"] = gitlab.is_tested(pipeline)
            pipeline["failed_tests"] = gitlab.failed_tests(pipeline)

            # get the application versions
            gitlab_versions = gitlab.application_versions(pipeline) or {}
            db_versions = db.get_versions(pipeline["id"]) or {}
            default_versions = {
                "sequencescape_version": UNKNOWN_VERSION,
                "limber_version": UNKNOWN_VERSION,
            }
            versions = {**default_versions, **db_versions, **gitlab_versions}
            pipeline["versions"] = versions

            # apply the versions to the failed tests for analysis
            for failed_test in pipeline["failed_tests"]:
                failed_test.int_suite_version = pipeline["int_suite_version"]
                failed_test.sequencescape_version = versions["sequencescape_version"]
                failed_test.limber_version = versions["limber_version"]

    except requests.exceptions.ConnectionError as e:
        # could not connect to gitlab instance, most likely not on the VPN
        print(e)
        pipelines = []

    # Analyse the failed tests
    # group pipelines by commitPath, versions.sequencescape_version, versions.limber_version
    # for each group, analyse the failed tests
    def group_pipelines(pipelines: List) -> Dict:
        grouped_pipelines = defaultdict(list)

        for pipeline in pipelines:
            key = (
                pipeline["commitPath"],
                pipeline["versions"]["sequencescape_version"],
                pipeline["versions"]["limber_version"],
            )
            if UNKNOWN_VERSION in key:
                continue  # Skip pipelines with None in the key
            if pipeline["is_tested"] is False:
                continue  # Skip pipelines where tests were not executed
            grouped_pipelines[key].append(pipeline)

        return grouped_pipelines

    flaky_tests = []
    for key, pipeline_group in group_pipelines(pipelines).items():
        if len(pipeline_group) == 1:
            continue  # Skip groups with only one pipeline

        # expect all tests within pipelines["failed_tests"] to be equal
        # if not, then the test is flaky and should be added to the flaky_tests list
        # create a list of sets of failed tests from each pipeline in the group
        failed_test_sets = [set(p["failed_tests"]) for p in pipeline_group]
        # find the difference of the failed tests
        flaky_tests.extend(set.difference(*failed_test_sets))

    return render_template(
        "index.jinja",
        pipelines=pipelines,
        flaky_tests=flaky_tests,
    )


@app.route("/new-pipeline/<int:pipeline_id>", methods=["GET"])
def new_pipeline(pipeline_id):
    lb_version = fetch_version(
        "https://uat.limber.psd.sanger.ac.uk/", ".version-info .container"
    )
    ss_version = fetch_version(
        "https://uat.sequencescape.psd.sanger.ac.uk/", ".deployment-info"
    )

    db.add_versions(pipeline_id, ss_version, lb_version)

    return "Captured application versions for pipeline {}\nSequenceScape: {}\nLimber: {}".format(
        pipeline_id, ss_version[0], lb_version[0]
    )
