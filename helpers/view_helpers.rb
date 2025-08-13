# frozen_string_literal: true

module ViewHelpers
  # Returns the pipeline duration in minutes, rounded up, or '?' if not available
  def pipeline_duration_minutes(pipeline)
    return '?' unless pipeline['duration']

    ((pipeline['duration'] / 60) + 1)
  end
end
