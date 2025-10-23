---
created_at: {{ pantheon_timestamp }}
created_by: {{ pantheon_actor }}
---
{% set _include_project_context = true %}
<!-- SECTION:START:PROJECT_CONTEXT -->
{% if _include_project_context %}
{% include 'artifact-template://update-architecture-guide/sections/project-context' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:PROJECT_CONTEXT -->

{% set _include_high_level_overview = true %}
<!-- SECTION:START:HIGH_LEVEL_OVERVIEW -->
{% if _include_high_level_overview %}
{% include 'artifact-template://update-architecture-guide/sections/high-level-overview' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:HIGH_LEVEL_OVERVIEW -->

{% set _include_core_principles = true %}
<!-- SECTION:START:CORE_PRINCIPLES -->
{% if _include_core_principles %}
{% include 'artifact-template://update-architecture-guide/sections/core-principles' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:CORE_PRINCIPLES -->

{% set _include_technology_stack = true %}
<!-- SECTION:START:TECHNOLOGY_STACK -->
{% if _include_technology_stack %}
{% include 'artifact-template://update-architecture-guide/sections/technology-stack' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:TECHNOLOGY_STACK -->

{% set _include_system_components = false %}
<!-- SECTION:START:SYSTEM_COMPONENTS -->
{% if _include_system_components %}
{% include 'artifact-template://update-architecture-guide/sections/system-components' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:SYSTEM_COMPONENTS -->

{% set _include_shared_services = false %}
<!-- SECTION:START:SHARED_SERVICES -->
{% if _include_shared_services %}
{% include 'artifact-template://update-architecture-guide/sections/shared-services' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:SHARED_SERVICES -->

{% set _include_implementation_patterns = false %}
<!-- SECTION:START:IMPLEMENTATION_PATTERNS -->
{% if _include_implementation_patterns %}
{% include 'artifact-template://update-architecture-guide/sections/implementation-patterns' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:IMPLEMENTATION_PATTERNS -->

{% set _include_testing_strategy = false %}
<!-- SECTION:START:TESTING_STRATEGY -->
{% if _include_testing_strategy %}
{% include 'artifact-template://update-architecture-guide/sections/testing-strategy' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:TESTING_STRATEGY -->

{% set _include_documentation_standards = true %}
<!-- SECTION:START:DOCUMENTATION_STANDARDS -->
{% if _include_documentation_standards %}
{% include 'artifact-template://update-architecture-guide/sections/documentation-standards' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:DOCUMENTATION_STANDARDS -->
