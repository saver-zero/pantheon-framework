---
created_at: {{ pantheon_timestamp }}
created_by: {{ pantheon_actor }}
---

{% set _include_ticket_description = true %}
<!-- SECTION:START:TICKET_DESCRIPTION -->
{% if _include_ticket_description %}
{% include 'artifact-template://update-kickoff-ticket/sections/ticket_description' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:TICKET_DESCRIPTION -->

{% if pantheon_active_profile.enable_progress_log %}

## Progress Log
{% set _include_progress_log = false %}
<!-- SECTION:START:PROGRESS_LOG -->
{% if _include_progress_log %}
{% include 'artifact-template://update-kickoff-ticket/sections/progress_log' %}
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
{% include 'artifact-template://update-kickoff-ticket/sections/commit_message' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:COMMIT_MESSAGE -->
{% endif %}
