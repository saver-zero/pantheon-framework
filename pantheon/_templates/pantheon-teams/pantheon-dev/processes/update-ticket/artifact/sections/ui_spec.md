## UI Spec

**Updated**: {{ pantheon_timestamp }}

**Updated By**: @{{ pantheon_actor }}

### ASCII Wireframe

```
{{ ascii_wireframe }}
```

### Layout Notes

{% for note in layout_notes %}
- {{ note }}
{% endfor %}

### Navigation Flow

```
{{ navigation_flow }}
```

### State Transitions
{% for t in state_transitions %}

**From:** {{ t.from_state }}
**To:** {{ t.to_state }}
**Trigger:** {{ t.trigger }}
**Visual change:** {{ t.visual_change }}

{% endfor %}

### Design Decision

**Decision**: {{ decision_title }}

**Rationale**: {{ rationale }}

**Alternatives Considered**:

{% for alt in alternatives %}
- **{{ alt.approach }}**: {{ alt.rejection_reason }}

{% endfor %}