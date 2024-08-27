import gitlab
import requests
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    try:
        pipelines = gitlab.query_pipelines()
        for pipeline in pipelines:
            # extract the number from the id gid://gitlab/Ci::Pipeline/286655
            pipeline["id"] = pipeline["id"].split("/")[-1]
            pipeline["commit_abbr"] = pipeline["commitPath"].split("/")[-1][:6]
            pipeline["failed_tests"] = gitlab.failed_tests(pipeline)

            gitlab_versions = gitlab.application_versions(pipeline) or {}
            default_versions = {
                "sequencescape": "&lt;unknown&gt;",
                "limber": "&lt;unknown&gt;",
            }
            versions = {**default_versions, **gitlab_versions}
            pipeline["versions"] = versions
    except requests.exceptions.ConnectionError as e:
        # could not connect to gitlab instance, most likely not on the VPN
        print(e)
        pipelines = []

    return render_template(
        "index.jinja",
        pipelines=pipelines,
    )
