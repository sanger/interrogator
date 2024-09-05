
import int_suite
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    filters = request.args  # get the query string parameters as the filters
    pipelines, flaky_tests = int_suite.compile_pipelines(**filters)
    return render_template("index.jinja", pipelines=pipelines, flaky_tests=flaky_tests)

