from collections import defaultdict
from typing import Dict, List

import db
import gitlab

UNKNOWN_VERSION = "&lt;unknown&gt;"


def group_pipelines(pipelines: List) -> Dict:
    """Group pipelines by commitPath, sequencescape_version, and limber_version."""
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


def extract_flaky_tests(pipelines: List) -> List:
    """Analyse pipelines to identify flaky tests."""
    # expect all tests within pipelines["failed_tests"] to be equal
    # if not, then the test is flaky and should be added to the flaky_tests list

    # create a list of sets of failed tests from each pipeline in the group
    failed_test_sets = [set(p["failed_tests"]) for p in pipelines]
    # find the difference of the failed tests
    flaky_test_set = set.union(*failed_test_sets) - set.intersection(*failed_test_sets)
    for flaky_test in flaky_test_set:
        flaky_test.is_flaky = True

    return flaky_test_set


def compile_pipelines(**filters):
    pipelines = gitlab.query_pipelines(**filters)
    for pipeline in pipelines:
        # extract the number from the id gid://gitlab/Ci::Pipeline/286655
        pipeline["id"] = pipeline["id"].split("/")[-1]
        pipeline["commit_abbr"] = pipeline["commitPath"].split("/")[-1][:6]
        pipeline["int_suite_version"] = f"{pipeline['ref']}@{pipeline['commit_abbr']}"
        pipeline["overall_status"] = gitlab.pipeline_status(pipeline)
        pipeline["is_tested"] = gitlab.is_tested(pipeline)
        pipeline["failed_tests"] = gitlab.failed_tests(pipeline)
        pipeline["job_times"] = gitlab.job_times(pipeline)

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

    flaky_tests = []
    for pipeline_group in group_pipelines(pipelines).values():
        if len(pipeline_group) == 1:
            continue  # Skip groups with only one pipeline
        flaky_tests.extend(extract_flaky_tests(pipeline_group))

    return pipelines, flaky_tests
