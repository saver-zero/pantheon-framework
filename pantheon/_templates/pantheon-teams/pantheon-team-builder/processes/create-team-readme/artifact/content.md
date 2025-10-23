---
created_at: {{ pantheon_timestamp }}
---
{% set _include_overview = true %}
<!-- SECTION:START:OVERVIEW -->
{% if _include_overview %}
{% include 'artifact-template://update-team-readme/sections/overview' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:OVERVIEW -->

{% set _include_getting_started = true %}
<!-- SECTION:START:GETTING_STARTED -->
{% if _include_getting_started %}
{% include 'artifact-template://update-team-readme/sections/getting_started' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:GETTING_STARTED -->

{% set _include_working_with_agents = true %}
<!-- SECTION:START:WORKING_WITH_AGENTS -->
{% if _include_working_with_agents %}
{% include 'artifact-template://update-team-readme/sections/working_with_agents' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:WORKING_WITH_AGENTS -->

{% set _include_agents = true %}
<!-- SECTION:START:AGENTS -->
{% if _include_agents %}
{% include 'artifact-template://update-team-readme/sections/agents' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:AGENTS -->

{% set _include_artifacts = true %}
<!-- SECTION:START:ARTIFACTS -->
{% if _include_artifacts %}
{% include 'artifact-template://update-team-readme/sections/artifacts' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:ARTIFACTS -->

{% set _include_workflow_examples = true %}
<!-- SECTION:START:WORKFLOW_EXAMPLES -->
{% if _include_workflow_examples %}
{% include 'artifact-template://update-team-readme/sections/workflow_examples' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:WORKFLOW_EXAMPLES -->
