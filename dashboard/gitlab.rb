# frozen_string_literal: true

require 'net/http'
require 'json'
require 'erb'
require 'logger'

GITLAB_URL = 'https://gitlab.internal.sanger.ac.uk'

GRAPHQL_TOKEN = File.read('gitlab.token').strip

module Gitlab
  class FailedTest
    attr_accessor :ref, :comment,:has_screenshot, :int_suite_version, :sequencescape_version, :limber_version, :is_flaky

    def initialize(location, description, job_url, has_screenshot)
      @ref = location
      @comment = description
      @job_url = job_url
      @has_screenshot = has_screenshot
      @int_suite_version = nil
      @sequencescape_version = nil
      @limber_version = nil
      @is_flaky = false
    end

    def screenshot_path
      artifacts_path = 'artifacts/file/tmp/capybara'
      filename = @ref.sub('./spec/', '').sub('.rb', '').gsub(%r{[/:]}, '_').concat('.png')
      "#{@job_url}/#{artifacts_path}/#{filename}"
    end
  end

  def self.query_pipelines(**filters)
    # Create a logger instance
    logger = Logger.new($stdout)

    # Set default values for filters
    first = filters[:first] || 20
    source = filters[:source] || 'all'
    status = filters[:status] || 'all'
    branch = filters[:branch] || 'all'

    template = File.read('dashboard/pipelines.gql')
    pipelines_filter = "first: #{first}"
    pipelines_filter += ", source: \"#{source}\"" if source && source != 'all'
    pipelines_filter += ", status: #{status.upcase}" if status && status != 'all'
    pipelines_filter += ", ref: \"#{branch}\"" if branch && branch != 'all'
    query = template.gsub('$pipelines_filter', pipelines_filter)

    uri = URI("#{GITLAB_URL}/api/graphql")
    headers = {
      'Authorization' => "Bearer #{GRAPHQL_TOKEN}",
      'Content-Type' => 'application/json'
    }
    parsed_response = nil
    begin
      response = Net::HTTP.post(uri, { query: }.to_json, headers)
      parsed_response = JSON.parse(response.body)
      if parsed_response['errors']
        logger.error(parsed_response['errors']) # Log the errors
        return []
      end
    rescue Errno::ECONNREFUSED, SocketError => e
      # could not connect to gitlab instance, most likely not on the VPN
      logger.error(e) # Log the errors
      return []
    end

    pipelines = []
    begin
      data = parsed_response
      pipelines = data['data']['project']['pipelines']['edges'].map do |edge|
        # collapse edges and nodes
        node = edge['node']
        node['jobs'] = node['jobs']['edges'].map do |job_edge|
          job_node = job_edge['node']
          job_node['artifacts'] = job_node['artifacts']['nodes']
          job_node
        end
        node
      end
    rescue KeyError
      # no pipelines found
      pipelines = []
    end
    pipelines
  end

  def self.is_lint(pipeline)
    pipeline['jobs'].any? { |job| job['name'] == 'job_lint' }
  end

  def self.pipeline_build_status(pipeline)
    job = pipeline['jobs'].find { |job| job['name'] == 'job_build' }
    job ? job['status'] : 'No build'
  end

  def self.pipeline_cleanup_status(pipeline)
    job = pipeline['jobs'].find { |job| job['name'] == 'job_cleanup' }
    job ? job['status'] : 'No cleanup'
  end

  def self.is_tested(pipeline)
    pipeline['jobs'].any? { |job| job['name'].start_with?('job_test') }
  end

  def self.extract_failed_tests(summary)
    regex = %r{(<br/>rspec \./[^<]+)}
    matches = summary.scan(regex).flatten
    matches.empty? ? [] : matches.join.split('<br/>')[1..]
  end

  def self.failed_tests(pipeline)
    failed_tests = []
    pipeline['jobs'].each do |job|
      next unless job['trace'] && job['trace']['htmlSummary'].include?('Failed examples:')

      extract_failed_tests(job['trace']['htmlSummary']).each do |test|
        location, description = *test[6..].split(' # ')
        job_url = "#{GITLAB_URL}#{job['webPath']}"
        has_screenshot = job['artifacts'].any? { |artifact| artifact['fileType'] == 'ARCHIVE' }
        failed_tests << FailedTest.new(location, description, job_url, has_screenshot) if test
      end
    end
    failed_tests
  end

  def self.format_duration(duration)
    return 'unknown' if duration.nil?

    "#{duration / 60}m #{duration % 60}s"
  end

  def self.job_times(pipeline)
    pipeline['jobs'].reverse.map { |job| "#{job['name']}: #{format_duration(job['duration'])}" }.join("\n")
  end

  def self.pipeline_status(pipeline)
    return "lint #{pipeline['status']}" if is_lint(pipeline)

    if pipeline['status'].downcase == 'failed'
      return 'build failed' if pipeline_build_status(pipeline).downcase == 'failed'
      return "tests failed (#{failed_tests(pipeline).size})" if failed_tests(pipeline).any?
      return 'cleanup failed' if pipeline_cleanup_status(pipeline).downcase == 'failed'
    end
    pipeline['status']
  end

  def self.extract_application_versions(html_summary)
    versions = {}
    if html_summary.include?('Application versions')
      regex = %r{Application versions deployed in \w+ environment:(.*)<br/><br/>}
      match = html_summary.match(regex)
      if match
        match[1].strip.split('<br/>').each do |line|
          next unless line.start_with?('  ')

          parts = line.strip.split(' ')
          app = parts[0].downcase
          version = parts[1..].join(' ')
          versions[app] = version
        end
      end
    end
    versions
  end

  def self.application_versions(pipeline)
    versions = {}
    pipeline['jobs'].each do |job|
      html_summary = job['trace'] ? job['trace']['htmlSummary'] : ''
      next unless html_summary.include?('Application versions')

      new_versions = extract_application_versions(html_summary)
      new_versions.each do |key, new_value|
        versions[key] = if versions[key] && versions[key] != new_value
                          'version changed during test run'
                        else
                          new_value
                        end
      end
    end
    versions
  end
end
