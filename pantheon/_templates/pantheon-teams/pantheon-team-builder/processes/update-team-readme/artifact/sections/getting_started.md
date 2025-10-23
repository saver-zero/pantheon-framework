## Getting Started

{{ quick_start_intro }}

### Prerequisites

{% for prerequisite in prerequisites %}
- {{ prerequisite }}
{% endfor %}

### Your First Interaction

{% for step in first_steps %}
**Step {{ loop.index }}: {{ step.title }}**

{{ step.instruction }}

{% if step.example %}
Example:

```

{{ step.example }}

```
{% endif %}

{% if step.tip %}
💡 **Tip**: {{ step.tip }}
{% endif %}

{% endfor %}

### What Happens Next

{{ next_steps }}

### Common Questions

{% for qa in common_questions %}
**Q: {{ qa.question }}**

A: {{ qa.answer }}

{% endfor %}
**Q: Is Pantheon a task management system?**

A: No, Pantheon doesn't position itself as a task management system, nor dictate a specific task management system. You can integrate any task management system of your choice simply by creating tasks based on the created artifacts.