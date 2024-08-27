from textwrap import dedent

import pytest

from dashboard.gitlab import application_versions


class TestApplicationVersions:
    @pytest.fixture
    def application_version_summary(self):
        return dedent(
            """
            1 example, 0 failures, 1 pending<br/>
            <br/>
            Application versions deployed in uat environment:<br/>
              Sequencescape ~sequencescape-version~<br/>
              Limber ~limber-version~<br/>
            <br/>
            Randomized with seed<br/>
            """
        ).replace("\n", "")

    def test_extract_application_versions(self, application_version_summary):
        pipeline = {"jobs": [{"trace": {"htmlSummary": application_version_summary}}]}
        result = application_versions(pipeline)
        assert result == {
            "Sequencescape": "~sequencescape-version~",
            "Limber": "~limber-version~",
        }

    def test_extraction_application_versions_when_no_htmlSummary(self):
        pipeline = {"jobs": [{"trace": {}}]}
        result = application_versions(pipeline)
        assert result == {}

    def test_extraction_application_versions_when_no_application_versions(self):
        pipeline = {
            "jobs": [{"trace": {"htmlSummary": "No application versions here."}}]
        }
        result = application_versions(pipeline)
        assert result == {}

    def test_extraction_application_versions_when_multiple_jobs_agree(
        self, application_version_summary
    ):
        pipeline = {
            "jobs": [
                {"trace": {"htmlSummary": application_version_summary}},
                {"trace": {"htmlSummary": application_version_summary}},
            ]
        }
        result = application_versions(pipeline)
        assert result == {
            "Sequencescape": "~sequencescape-version~",
            "Limber": "~limber-version~",
        }

    def test_extraction_application_versions_when_multiple_jobs_differ(
        self, application_version_summary
    ):
        application_version_summary_different = application_version_summary.replace(
            "~sequencescape-version~", "v14.41.0-10509115791-develop@a601903"
        )
        pipeline = {
            "jobs": [
                {"trace": {"htmlSummary": application_version_summary}},
                {"trace": {"htmlSummary": application_version_summary_different}},
            ]
        }
        result = application_versions(pipeline)
        assert result == {
            "Limber": "~limber-version~",
            "Sequencescape": "version changed during test run",
        }
