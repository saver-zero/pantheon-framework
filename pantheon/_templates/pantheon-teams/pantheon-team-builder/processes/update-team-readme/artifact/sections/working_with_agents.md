{% set team_name = team_name | slugify | remove_suffix("-team") %}
## Working with {{ team_name }} Agents

The {{ team_name }} team operates through natural conversation with agents, not technical commands. Each agent is an expert in their domain who understands your goals and translates them into concrete artifacts: {{ artifact_types | map(attribute='name') | join(', ') }}.

You communicate directly with agents using plain language about what you want to accomplish. Working through the agents eliminates the cognitive overhead of remembering complex procedures and technical syntax.

Agents maintain consistent behavior through structured processes provided by the Pantheon framework, ensuring reliable results every time. This systematic approach creates clear accountability and traceability, so it’s always obvious what was done and why.

With every action documented in structured artifacts and audit trails, you gain full transparency, while staying focused on high-level direction and decision-making.

### Your Role

{{ human_role }}

Once you have the artifacts, direct the primary LLM agent outside of Pantheon (i.e. Claude Code, GPT Codex, Gemini) to execute based on the artifact (i.e. implement code based on plan, write blog post based on outline). This allows for a flexible collaboration between the main LLM agent based on the artifacts created: {{ artifact_types | map(attribute='name') | join(', ') }} .

### Communication Best Practices

{% for practice in best_practices %}
- **{{ practice.principle }}**: {{ practice.explanation }}
{% endfor %}