---
created_at: {{ pantheon_timestamp }}
---
{% set team_name = target_team | slugify | remove_suffix("-team") %}
{% if pantheon_artifact_id is not string or not pantheon_artifact_id.startswith('TB') %}
{% set pantheon_artifact_id = "TB{:02d}".format(pantheon_artifact_id|int) %}
{% endif %}
<!--
## Welcome to Your Blueprint Journey

Think of this file as a shared workspace that you and the specialist agents shape together. Every time you collaborate with them, each section of the blueprint will be drafted in place of a `SECTION:PLACEHOLDER` tag. Move at your own pace, review the drafts they hand back, and keep iterating until the blueprint feels like it truly represents the team you have in mind.

### Phase 1: Shape the Blueprint Together (Iterative)

This phase is all about conversations and refinement. Each interaction gives the agents more context, and each revision brings the blueprint closer to what you need. For this phase, you need to refer to the blueprint using the blueprint ID (i.e {{ pantheon_artifact_id }}).

1.  **Set the Strategy & Context**
    -   **Who to chat with:** `@pantheon-team-builder`
    -   **Try asking:** @pantheon-team-builder, create the strategy and context for a new team based on the workflow in @docs/workflows/my-new-workflow.md
    -   The agent will help bring the `Overall Strategy` and `Project Context` sections to life. Review and provide feedback to @pantheon-team-builder to make any updates, or make the updates yourself in the doc directly.

2.  **Design the Artifacts**
    -   **Who to chat with:** `@artifact-designer`
    -   **Try asking:** @artifact-designer, design the artifacts for {{ pantheon_artifact_id }} and update the team blueprint. Do not build the artifacts yet, focus on updating the team blueprint with the artifact design.
    -   The placeholders under `ARTIFACTS` will evolve into a detailed design you can react to. Review it and provide feedback to the @artifact-designer to make any updates, or make the updates yourself in the doc directly.

3.  **Design the Agents**
    -   **Who to chat with:** `@agent-designer`
    -   **Try asking:** @agent-designer, design the agents for {{ pantheon_artifact_id }} and update the team blueprint. Do not build the agents yet, focus on updating the team blueprint with the agent design.
    -   The agent architecture will gradually replace the `AGENTS` section as you iterate together. Review it and provide feedback to the @agent-designer to make any updates, or make the updates yourself in the doc directly.

4.  **Create the Team Readme**
    -   **Who to chat with:** `@team-readme-writer`
    -   **Try asking:** @team-readme-writer, create the team readme based on @[{{ pantheon_artifact_id }}]_{{ target_team | lower | replace(' ', '-') }}_team-blueprint.md
    -   The team-readme-writer will create a team readme. Review and provide feedback to the readme writer to update any flows or usages you'd like to change. And point to the read me to have artifact-designer and agent-designer update their relevant sections of the blueprint.

5.  **Loop, Compare, Refine**
    -   Use what the @agent-designer creates to check whether the artifacts still make sense. If anything feels off, circle back to the @artifact-designer and explore a revised idea.

6.  **Finish with the Team Profile**
    -   **Who to chat with:** `@profile-designer`
    -   **Try asking:** @profile-designer, design the team profile for the blueprint {{ pantheon_artifact_id }}
    -   Together you will turn the `PROFILE` placeholder into the configuration that ties everything together. Review it and provide feedback to the @profile-designer to make any updates, or make the updates yourself in the doc directly.
    -   You do not have to use or implement any of the profiles or configs, if you prefer to keep things simple. In that case, just delete the profiles and replace with "No profiles or configs needed".

### Phase 2: Bring the Blueprint to Life (Sequential)

Once the blueprint feels complete, you can use it as a script for creating the real team package. These steps happen in order so each piece has what it needs from the previous one. For this phase, you can refer to the blueprint using the full filename (i.e. [{{ pantheon_artifact_id }}]_{{ target_team | lower | replace(' ', '-') }}_team-blueprint.md])

1.  **Create the Team Profile**
    -   The profile carries shared configuration that other components lean on.
    -   i.e @profile-designer create the team profile from @[{{ pantheon_artifact_id }}]_{{ target_team | lower | replace(' ', '-') }}_team-blueprint.md

2.  **Stand Up the Agents**
    -   Agents need to exist so the later processes know who they are empowering.
    -   For each agent described here, ask @agent-designer to create the agent from the blueprint.
    -   i.e @agent-designer create the agents from @[{{ pantheon_artifact_id }}]_{{ target_team | lower | replace(' ', '-') }}_team-blueprint.md
    -   Review it and provide feedback to the @agent-designer to make any updates, or make the updates yourself in the generated agent prompt directly.

3.  **Build the Artifacts & Processes**
    -   This step turns the blueprint's core workflows into the files your team will actually run.
    -   For each artifact, request the @artifact-designer to build each artifact
    -   i.e @artifact-designer, build the artifacts from @[{{ pantheon_artifact_id }}]_{{ target_team | lower | replace(' ', '-') }}_team-blueprint.md
    -   Review it and provide feedback to the @artifact-designer to make any updates, or make the updates yourself in the generated processes and artifact schemas and templates directly.

When you've walked through these steps, the new team package is ready for its debut.
-->
{% set _include_foundation = true %}
<!-- SECTION:START:FOUNDATION -->
{% if _include_foundation %}
{% include 'artifact-template://update-team-blueprint/sections/foundation' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:FOUNDATION -->

{% set _include_context = true %}
<!-- SECTION:START:CONTEXT -->
{% if _include_context %}
{% include 'artifact-template://update-team-blueprint/sections/context' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:CONTEXT -->

{% set _include_artifacts = false %}
<!-- SECTION:START:ARTIFACTS -->
{% if _include_artifacts %}
{% include 'artifact-template://update-team-blueprint/sections/artifacts' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:ARTIFACTS -->

{% set _include_agents = false %}
<!-- SECTION:START:AGENTS -->
{% if _include_agents %}
{% include 'artifact-template://update-team-blueprint/sections/agents' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:AGENTS -->

{% set _include_profile = false %}
<!-- SECTION:START:PROFILE -->
{% if _include_profile %}
{% include 'artifact-template://update-team-blueprint/sections/profile' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:PROFILE -->
