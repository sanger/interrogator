# frozen_string_literal: true

require 'cgi'
require 'set'
require_relative 'gitlab'

UNKNOWN_VERSION = CGI.escapeHTML('<unknown>')

module IntSuite
  def self.group_pipelines(pipelines)
    # Group pipelines by int_suite, sequencescape, and limber versions.
    grouped_pipelines = Hash.new { |hash, key| hash[key] = [] }

    pipelines.each do |pipeline|
      key = [
        pipeline['versions']['int_suite'],
        pipeline['versions']['sequencescape'],
        pipeline['versions']['limber']
      ]

      next if key.include?(UNKNOWN_VERSION)  # Skip pipelines with unknown versions
      next unless pipeline['is_tested']      # Skip pipelines where tests were not executed

      grouped_pipelines[key] << pipeline
    end

    grouped_pipelines
  end

  def self.extract_flaky_tests(pipelines)
    # Analyse pipelines to identify flaky tests.
    # Expect all tests within pipelines["failed_tests"] to be equal.
    # If not, then the test is flaky and should be added to the flaky_tests list.

    # Create a list of sets of failed tests from each pipeline in the group
    failed_test_sets = pipelines.map { |p| p['failed_tests'].to_set }

    # Find the difference of the failed tests
    flaky_test_set = failed_test_sets.reduce(:|) - failed_test_sets.reduce(:&)

    flaky_test_set.each { |flaky_test| flaky_test.is_flaky = true }

    flaky_test_set.to_a
  end

  def self.compile_pipelines(filters = {})
    pipelines = Gitlab.query_pipelines(**filters)

    pipelines.each do |pipeline|
      # Extract the number from the id gid://gitlab/Ci::Pipeline/286655
      pipeline['id'] = pipeline['id'].split('/').last
      pipeline['commit_abbr'] = pipeline['commitPath'].split('/').last[0, 6]
      pipeline['int_suite_version'] = "#{pipeline['ref']}@#{pipeline['commit_abbr']}"
      pipeline['overall_status'] = Gitlab.pipeline_status(pipeline)
      pipeline['is_tested'] = Gitlab.is_tested(pipeline)
      pipeline['failed_tests'] = Gitlab.failed_tests(pipeline)
      pipeline['job_times'] = Gitlab.job_times(pipeline)

      # Get the application versions
      gitlab_versions = Gitlab.application_versions(pipeline) || {}
      default_versions = {
        'int_suite' => pipeline['int_suite_version'],
        'sequencescape' => UNKNOWN_VERSION,
        'limber' => UNKNOWN_VERSION
      }
      versions = default_versions.merge(gitlab_versions)
      pipeline['versions'] = versions

      # Apply the versions to the failed tests for analysis
      pipeline['failed_tests'].each do |failed_test|
        failed_test.int_suite_version = versions['int_suite']
        failed_test.sequencescape_version = versions['sequencescape']
        failed_test.limber_version = versions['limber']
      end
    end

    flaky_tests = []
    group_pipelines(pipelines).each_value do |pipeline_group|
      next if pipeline_group.length == 1 # Skip groups with only one pipeline

      flaky_tests.concat(extract_flaky_tests(pipeline_group))
    end

    [pipelines, flaky_tests]
  end
end
