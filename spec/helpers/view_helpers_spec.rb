# frozen_string_literal: true

require 'rspec'
require './helpers/view_helpers'

RSpec.describe ViewHelpers do
  let(:helper) { Class.new { extend ViewHelpers } }

  describe '#pipeline_duration_minutes' do
    let(:pipeline) { build(:pipeline, duration: (23 * 60) + 30) }

    context 'when duration is nil' do
      let(:pipeline) { build(:pipeline, duration: nil) }

      it 'returns "?"' do
        expect(helper.pipeline_duration_minutes(pipeline)).to eq('?')
      end
    end

    it 'returns the duration in minutes rounded up' do
      expect(helper.pipeline_duration_minutes(pipeline)).to eq(24)
    end
  end

  describe '#test_duration_minutes' do
    let(:pipeline) { build(:pipeline, jobs: jobs) }

    context 'when no test jobs are present' do
      let(:jobs) { [] }

      it 'returns nil' do
        expect(helper.test_duration_minutes(pipeline)).to be_nil
      end
    end

    context 'when test jobs are present' do
      let(:jobs) do
        [
          { 'name' => 'test_job_1', 'duration' => 120 },
          { 'name' => 'test_job_2', 'duration' => 181 }
        ]
      end

      it 'returns the maximum test duration in minutes rounded up' do
        expect(helper.test_duration_minutes(pipeline)).to eq(4)
      end
    end
  end
end
