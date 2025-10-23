## Core Principles
last updated: {{ pantheon_timestamp }}
updated by: {{ pantheon_actor }}

{% for principle in principles %}
### {{ principle.name }}

**Principle**: {{ principle.statement }}

**Rationale**: {{ principle.rationale }}

**Examples**:
{% for example in principle.examples %}
- {{ example }}
{% endfor %}

{% endfor %}

## Anti-Patterns

{% for antipattern in antipatterns %}
### {{ antipattern.name }}

**What to Avoid**: {{ antipattern.description }}

**Why It's Problematic**: {{ antipattern.problems }}

**Instead, Do This**: {{ antipattern.alternative }}

{% endfor %}