# frozen_string_literal: true

require 'time'
require 'faker'

FactoryBot.define do
  factory :pipeline, class: Hash do
    initialize_with { attributes.stringify_keys }

    source { 'schedule' }
    createdAt { Time.now.iso8601 }
    status { 'FAILED' }
    duration { 3000 }
    commitPath { '/psd/integration-suite/-/commit/99e08b3755f8a8c497d83190bf55701831e16fa2' }
    ref { 'master' }
    commit_abbr { '99e08b' } # Faker::Number.hexadecimal(digits: 6)
    int_suite_version { "#{ref}@#{commit_abbr}" }
    overall_status { 'tests failed (1)' }
    tested? { true }
    job_times do
      <<~JOB_TIMES
        job_build: 2m 49s
        job_test 1/4: 23m 28s
        job_test 2/4: 14m 26s
        job_test 3/4: 36m 13s
        job_test 4/4: 46m 56s
        job_cleanup: unknown
      JOB_TIMES
    end
    versions do
      {
        'environment' => 'uat',
        'int_suite' => int_suite_version.to_s,
        'sequencescape' => 'v14.48.0-11775359715-develop@b447eef',
        'limber' => 'y24-335-uat@6ce02b7'
      }
    end

    factory :pipeline1 do
      jobs do
        [
          { 'id' => 'gid://gitlab/Ci::Build/1680850',
            'name' => 'job_cleanup',
            'status' => 'SKIPPED',
            'kind' => 'BUILD',
            'webPath' => '/psd/integration-suite/-/jobs/1680850',
            'duration' => nil,
            'trace' => nil,
            'artifacts' => [] },
          { 'id' => 'gid://gitlab/Ci::Build/1680848',
            'name' => 'job_test 4/4',
            'status' => 'FAILED',
            'kind' => 'BUILD',
            'webPath' => '/psd/integration-suite/-/jobs/1680848',
            'duration' => 2816,
            'trace' => { 'htmlSummary' => '~htmlSummary~' },
            'artifacts' => [
              { 'id' => 'gid://gitlab/Ci::JobArtifact/1464853',
                'name' => 'job.log',
                'fileType' => 'TRACE',
                'downloadPath' => '/psd/integration-suite/-/jobs/1680848/artifacts/download?file_type=trace' },
              { 'id' => 'gid://gitlab/Ci::JobArtifact/1464852',
                'name' => 'metadata.gz',
                'fileType' => 'METADATA',
                'downloadPath' => '/psd/integration-suite/-/jobs/1680848/artifacts/download?file_type=metadata' },
              { 'id' => 'gid://gitlab/Ci::JobArtifact/1464851',
                'name' => 'artifacts.zip',
                'fileType' => 'ARCHIVE',
                'downloadPath' => '/psd/integration-suite/-/jobs/1680848/artifacts/download?file_type=archive' }
            ] }
        ]
      end
      failed_tests { [build(:failed_test)] }
    end

    factory :pipeline2 do
      jobs do
        [
          { 'id' => 'gid://gitlab/Ci::Build/1678638',
            'name' => 'job_cleanup',
            'status' => 'SKIPPED',
            'kind' => 'BUILD',
            'webPath' => '/psd/integration-suite/-/jobs/1678638',
            'duration' => nil,
            'trace' => nil,
            'artifacts' => [] },
          { 'id' => 'gid://gitlab/Ci::Build/1678636',
            'name' => 'job_test 4/4',
            'status' => 'FAILED',
            'kind' => 'BUILD',
            'webPath' => '/psd/integration-suite/-/jobs/1678636',
            'duration' => 3002,
            'trace' => { 'htmlSummary' => '~htmlSummary~' },
            'artifacts' => [
              { 'id' => 'gid://gitlab/Ci::JobArtifact/1462429',
                'name' => 'job.log',
                'fileType' => 'TRACE',
                'downloadPath' => '/psd/integration-suite/-/jobs/1678636/artifacts/download?file_type=trace' },
              { 'id' => 'gid://gitlab/Ci::JobArtifact/1462427',
                'name' => 'metadata.gz',
                'fileType' => 'METADATA',
                'downloadPath' => '/psd/integration-suite/-/jobs/1678636/artifacts/download?file_type=metadata' },
              { 'id' => 'gid://gitlab/Ci::JobArtifact/1462426',
                'name' => 'artifacts.zip',
                'fileType' => 'ARCHIVE',
                'downloadPath' => '/psd/integration-suite/-/jobs/1678636/artifacts/download?file_type=archive' }
            ] }
        ]
      end
      failed_tests { [build(:failed_test)] }
    end

    factory :pipeline3 do
      jobs do
        [
          { 'id' => 'gid://gitlab/Ci::Build/1677095',
            'name' => 'job_test 4/4',
            'status' => 'FAILED',
            'kind' => 'BUILD',
            'webPath' => '/psd/integration-suite/-/jobs/1677095',
            'duration' => 2674,
            'trace' => { 'htmlSummary' => '~htmlSummary~' },
            'artifacts' => [
              { 'id' => 'gid://gitlab/Ci::JobArtifact/1460854',
                'name' => 'job.log',
                'fileType' => 'TRACE',
                'downloadPath' => '/psd/integration-suite/-/jobs/1677095/artifacts/download?file_type=trace' },
              { 'id' => 'gid://gitlab/Ci::JobArtifact/1460846',
                'name' => 'metadata.gz',
                'fileType' => 'METADATA',
                'downloadPath' => '/psd/integration-suite/-/jobs/1677095/artifacts/download?file_type=metadata' },
              { 'id' => 'gid://gitlab/Ci::JobArtifact/1460845',
                'name' => 'artifacts.zip',
                'fileType' => 'ARCHIVE',
                'downloadPath' => '/psd/integration-suite/-/jobs/1677095/artifacts/download?file_type=archive' }
            ] }
        ]
      end
      failed_tests { [build(:failed_test)] }
    end
  end
end
