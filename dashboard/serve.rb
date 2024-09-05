# frozen_string_literal: true

require 'sinatra'
require_relative 'int_suite'

set :public_folder, "#{__dir__}/static"

get '/' do
  pipelines, flaky_tests = IntSuite.compile_pipelines(params)
  erb :index, locals: { pipelines: pipelines, flaky_tests: flaky_tests }
end
