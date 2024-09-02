from pathlib import Path

import db
import int_suite
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
    pipelines, flaky_tests = int_suite.compile_pipelines(**filters)
    return render_template("index.jinja", pipelines=pipelines, flaky_tests=flaky_tests)


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
