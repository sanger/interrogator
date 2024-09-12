# frozen_string_literal: true

require 'sinatra'
require_relative 'integration_suite'

set :public_folder, "#{__dir__}/static"

get '/' do
  pipelines, flaky_tests = IntegrationSuite.compile_pipelines(params)
  branches = IntegrationSuite.branches(pipelines)
  erb :'index.html', locals: { gitlab_url: GITLAB_URL, pipelines:, flaky_tests:, branches: }
end
