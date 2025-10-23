# [{{ pantheon_timestamp }}] {{ target_agent }} Feedback

Feedback for: {{ target_agent }}
Feedback type: {{ feedback_type }}
Severity: {{ severity }}
User Sentiment: {{ user_sentiment }}

## What was the situation?
{{ situation_before }}

## What was the agent's behavior?
{{ agent_behavior_before }}

## What was the user's feedback?
{{ user_feedback }}

## Code Context
The feedback {% if contains_code %}had{% endif %}{% if not contains_code %}did not have any{% endif %} code snippets.

## What action did the agent take after?
{{ agent_action_taken }}
