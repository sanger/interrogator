from pathlib import Path

import db
import gitlab
import requests
from applications import fetch_version
from flask import Flask, render_template

app = Flask(__name__)
app.config.from_mapping(
    DATABASE=Path(app.root_path) / "dashboard.sqlite",
)
db.init_app(app)


@app.route("/")
def index():
    try:
        pipelines = gitlab.query_pipelines()
        for pipeline in pipelines:
            # extract the number from the id gid://gitlab/Ci::Pipeline/286655
            pipeline["id"] = pipeline["id"].split("/")[-1]
            pipeline["commit_abbr"] = pipeline["commitPath"].split("/")[-1][:6]
            pipeline["failed_tests_html"] = gitlab.failed_tests_html(pipeline)
            versions = db.get_versions(pipeline["id"])
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
