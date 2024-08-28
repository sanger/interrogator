from pathlib import Path

import db
import gitlab
import requests
from applications import fetch_version
from flask import Flask, render_template, request

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
            pipeline["overall_status"] = gitlab.pipeline_status(pipeline)
            pipeline["failed_tests"] = gitlab.failed_tests(pipeline)

            gitlab_versions = gitlab.application_versions(pipeline) or {}
            db_versions = db.get_versions(pipeline["id"]) or {}
            default_versions = {
                "sequencescape_version": "&lt;unknown&gt;",
                "limber_version": "&lt;unknown&gt;",
            }
            versions = {**default_versions, **db_versions, **gitlab_versions}
            pipeline["versions"] = versions
    except requests.exceptions.ConnectionError as e:
        # could not connect to gitlab instance, most likely not on the VPN
        print(e)
        pipelines = []

    return render_template(
        "index.jinja",
        pipelines=pipelines,
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
