# frozen_string_literal: true

require 'sinatra'
require_relative 'int_suite'

set :public_folder, "#{__dir__}/static"

get '/' do
  pipelines, flaky_tests = IntSuite.compile_pipelines(params)
  erb :'index.html', locals: { pipelines:, flaky_tests: }
end
