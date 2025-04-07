# frozen_string_literal: true

FactoryBot.define do
  factory :failed_test, class: 'Gitlab::FailedTest' do
    initialize_with { new(ref, comment, job_url, has_screenshot) }

    ref { './spec/limber/scrna_core_volume_spec.rb:1062' }
    comment do
      'Following the high throughput scRNA Core Cell Extraction pipeline scRNA Core entry point 1 ' \
        '- LRC Blood Vac tubes Blood Banking'
    end
    job_url { 'https://gitlab.internal.sanger.ac.uk/psd/integration-suite/-/jobs/1680848' }
    has_screenshot { true }

    factory :versioned_failed_test do
      environment { 'uat' }
      int_suite_version { 'master@99e08b' }
      sequencescape_version { 'v14.48.0-11775359715-develop@b447eef' }
      limber_version { 'y24-335-uat@6ce02b7' }

      factory :flaky_failed_test do
        is_flaky { true }
      end
    end
  end
end
