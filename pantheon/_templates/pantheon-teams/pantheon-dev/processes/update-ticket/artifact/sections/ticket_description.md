{% if pantheon_artifact_id is not string or not pantheon_artifact_id.startswith('T') %}
{% set pantheon_artifact_id = "T{:03d}".format(pantheon_artifact_id|int) %}
{% endif %}
# **Ticket {{ pantheon_artifact_id }}:** {{ title }}

## Metadata

*   **Ticket ID:** {{ pantheon_artifact_id }}
*   **Assigned to:** {{ assignee }}
{% if senior_assignment_rationale %}
    * **Senior assignment rationale:** {{ senior_assignment_rationale }}
{% endif %}
*   **Priority:** P{{ priority }}
*   **Last updated:** {{ pantheon_timestamp }}
*   **Created by:** {{ pantheon_actor }}
{% if dependencies %}
*   **Dependencies:** {{ dependencies }}
{% endif %}

## 🎯 Objective
{{ objective }}

---

## 📚 Architectural Context & References

### **1. Relevant Documentation & Diagrams**
{% if relevant_documentation %}{% for doc in relevant_documentation %}
{% if doc.documentation_type == "COMMAND" %}
*   **Use `{{ doc.path }}`**: {{ doc.relevance }}
{% else %}
*   **[{{ doc.path }}]({{ doc.path }})**: {{ doc.relevance }}
{% endif %}
{% endfor %}{% else %}
*   *No specific documentation was flagged as essential for this ticket.*
{% endif %}

### **2. Key Design Patterns & Principles**
{% if design_patterns %}{% for pat in design_patterns %}
*   **{{ pat.pattern }}**: {{ pat.rationale }}
{% endfor %}{% else %}
*   *No specific design patterns were highlighted for this ticket.*
{% endif %}
{% if constraints_and_anti_patterns %}

### **3. Constraints & Anti-Patterns to Avoid**
{% for constraint in constraints_and_anti_patterns %}
*   {{ constraint }}
{% endfor %}{% endif %}

---

## ✅ Success Criteria

### **1. Additional Context**

{{ context }}

### **2. Acceptance Criteria**
{% if acceptance_criteria %}{% for ac in acceptance_criteria %}
*   **As a** {{ ac.persona }}, **I want to** {{ ac.action }}, **so that** {{ ac.benefit }}.
{% endfor %}{% endif %}
