# frozen_string_literal: true

# Provides utility methods for formatting and extracting
# pipeline and job information for use in view templates.
module ViewHelpers
  # Returns the pipeline duration in minutes, rounded up, or '?' if not available
  def pipeline_duration_minutes(pipeline)
    return '?' unless pipeline['duration']

    (pipeline['duration'] / 60.0).ceil.to_i
  end

  # Returns the test duration in minutes, or nil if not available
  def test_duration_minutes(pipeline)
    pipeline['jobs']
      .select { |job| job['name'].include?('test') && job['duration'] }
      .map { |job| (job['duration'] / 60.0).ceil.to_i }
      .max
  end
end
