---
created_at: {{ pantheon_timestamp }}
---
{% set _include_ticket_description = true %}
<!-- SECTION:START:TICKET_DESCRIPTION -->
{% if _include_ticket_description %}
{% include 'artifact-template://update-ticket/sections/ticket_description' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:TICKET_DESCRIPTION -->
{% if pantheon_active_profile.perform_code_review %}

{% set _include_baseline_commit = false %}
<!-- SECTION:START:BASELINE_COMMIT -->
{% if _include_baseline_commit %}
{% include 'artifact-template://update-ticket/sections/baseline_commit' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:BASELINE_COMMIT -->
{% endif %}

{% set _include_technical_plan = false %}
<!-- SECTION:START:TECHNICAL_PLAN -->
{% if _include_technical_plan %}
{% include 'artifact-template://update-ticket/sections/technical_plan' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:TECHNICAL_PLAN -->

{% if pantheon_active_profile.enable_progress_log %}

## Progress Log
{% set _include_progress_log = false %}
<!-- SECTION:START:PROGRESS_LOG -->
{% if _include_progress_log %}
{% include 'artifact-template://update-ticket/sections/progress_log' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:PROGRESS_LOG -->
{% endif %}
{% if pantheon_active_profile.draft_commit_message %}

## Commit Message
{% set _include_commit_message = false %}
<!-- SECTION:START:COMMIT_MESSAGE -->
{% if _include_commit_message %}
{% include 'artifact-template://update-ticket/sections/commit_message' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:COMMIT_MESSAGE -->
{% endif %}
{% if pantheon_active_profile.perform_code_review %}

## Code Review
{% set _include_code_review = false %}
<!-- SECTION:START:CODE_REVIEW -->
{% if _include_code_review %}
{% include 'artifact-template://update-ticket/sections/code_review' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:CODE_REVIEW -->
{% endif %}