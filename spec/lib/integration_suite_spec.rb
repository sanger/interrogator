# frozen_string_literal: true

require 'rspec'
require 'set'
require './lib/integration_suite'

RSpec.describe IntegrationSuite do
  describe '.extract_flaky_tests' do
    let(:failing_test) { build(:versioned_failed_test, ref: 'failing', environment: 'uat') }
    let(:flaky_test) { build(:versioned_failed_test, ref: 'flaky', environment: 'uat') }

    let(:pipelines) do
      [build(:pipeline1, failed_tests: [failing_test]),
       build(:pipeline2, failed_tests: [failing_test, flaky_test]),
       build(:pipeline3, failed_tests: [failing_test])]
    end

    context 'when identifying flaky tests' do
      let(:flaky_tests) { described_class.extract_flaky_tests(pipelines) }

      it 'includes flaky test in flaky_test' do
        expect(flaky_tests).to include(flaky_test)
      end

      it 'marks flaky_test as flaky' do
        extracted_flaky_test = flaky_tests.find { |test| test == flaky_test }
        expect(extracted_flaky_test.is_flaky).to be true
      end

      it 'does not include the consistently failing test in flaky_test' do
        expect(flaky_tests).not_to include(failing_test)
      end
    end
  end
end
