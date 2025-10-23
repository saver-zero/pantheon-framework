---
doc_id: security-permissions-system
title: "Permission System Structure"
description: "Detailed guide to permission file structure, process-level and section-level permissions, and wildcard patterns."
keywords: [permissions, permissions-jsonnet, process-level, section-level, wildcard, access-control]
relevance: "Use this document to understand how to structure permission files for processes, including process-level, section-level, and wildcard permissions."
---

# Permission System Structure

This document provides a comprehensive guide to structuring `permissions.jsonnet` files for controlling access to processes and their sections.

## Permission File Location

Every process **must** include a `permissions.jsonnet` file:

```
processes/<process-name>/
├── routine.md
├── permissions.jsonnet    # Required
├── schema.jsonnet
└── artifact/
```

Missing permission files result in access denial for all actors.

## Basic Permission Structure

### Minimal Configuration
```jsonnet
{
  "allow": ["actor-name"],
  "deny": []
}
```

### Complete Configuration
```jsonnet
{
  // Process-level permissions (required)
  "allow": ["actor1", "actor2"],
  "deny": ["deprecated-actor"],

  // Section-level permissions (optional)
  "sections": {
    "section-name": {
      "allow": ["specialist-actor"],
      "deny": []
    }
  }
}
```

## Process-Level Permissions

Process-level permissions control access to the entire process, regardless of operation type.

### Required Fields
- **`allow`** (array of strings): List of actors who can execute this process
- **`deny`** (array of strings): List of actors explicitly denied access

### Examples

**Single Owner:**
```jsonnet
{
  "allow": ["tech-lead"],
  "deny": []
}
```

**Multiple Owners:**
```jsonnet
{
  "allow": ["tech-lead", "senior-developer", "product-manager"],
  "deny": []
}
```

**With Exclusions:**
```jsonnet
{
  "allow": ["tech-lead", "developer"],
  "deny": ["junior-developer", "deprecated-agent"]
}
```

## Section-Level Permissions

Section-level permissions enable fine-grained control over UPDATE operations, allowing different actors to modify different parts of an artifact.

### Structure
```jsonnet
{
  "allow": ["admin"],  // Process-level baseline
  "sections": {
    "section_name": {
      "allow": ["specialist"],
      "deny": []
    }
  }
}
```

### Multi-Section Example
```jsonnet
{
  "allow": ["pantheon"],  // Admin override for all sections
  "sections": {
    "requirements": {
      "allow": ["product-manager", "business-analyst"],
      "deny": []
    },
    "technical_design": {
      "allow": ["architect", "tech-lead"],
      "deny": []
    },
    "implementation_plan": {
      "allow": ["senior-developer", "tech-lead"],
      "deny": []
    },
    "test_strategy": {
      "allow": ["qa-engineer", "test-lead"],
      "deny": []
    },
    "deployment": {
      "allow": ["devops", "sre"],
      "deny": []
    }
  }
}
```

### Section Permission Inheritance

Section-level permissions are **additive** with process-level permissions:

```jsonnet
{
  "allow": ["admin"],  // Admin has baseline access
  "sections": {
    "code_review": {
      "allow": ["senior-developer"],  // Adds to admin access
      "deny": []
    }
  }
}
```

**Result**: Both `admin` AND `senior-developer` can update the "code_review" section (union of allows).

### Section-Only Access

Processes can have no baseline access, requiring section-specific permissions:

```jsonnet
{
  "allow": [],  // No default access
  "deny": [],
  "sections": {
    "public": {
      "allow": ["*"],  // Everyone can access public
      "deny": []
    },
    "private": {
      "allow": ["team-lead"],  // Only team-lead for private
      "deny": []
    }
  }
}
```

## Wildcard Permissions

### Universal Access Pattern

Use `"*"` to grant access to everyone:

```jsonnet
{
  "allow": ["*"],  // Everyone can access
  "deny": []
}
```

### Wildcards with Exclusions

Combine wildcards with explicit denials:

```jsonnet
{
  "allow": ["*"],
  "deny": ["guest", "external-auditor"]
}
```

### Section-Level Wildcards

```jsonnet
{
  "allow": ["admin"],  // Admin has full access
  "sections": {
    "public_notes": {
      "allow": ["*"],  // Everyone can edit public notes
      "deny": []
    },
    "team_config": {
      "allow": ["tech-lead"],  // Restricted access
      "deny": []
    }
  }
}
```

### When to Use Wildcards

**Appropriate Uses:**
- Public processes (documentation, general notes)
- Collaboration areas (brainstorming, shared planning)
- Development environments (relaxed restrictions for experimentation)

**Security Note:** Always use explicit deny lists with wildcards to exclude specific actors.

## Permission Inheritance and Additive Model

### Process-Level Allow as Baseline

Process-level `allow` grants baseline access to all sections:

```jsonnet
{
  "allow": ["admin", "tech-lead"],  // Baseline for all sections
  "sections": {
    "technical": {
      "allow": ["developer"],  // Adds developer access
      "deny": []
    }
  }
}
```

**Result:**
- "technical" section: `admin OR tech-lead OR developer`
- Other sections: `admin OR tech-lead`

### Additive Union Principle

Actors gain access if they're in **either** process OR section allow lists:

```jsonnet
{
  "allow": ["A"],
  "sections": {
    "s1": { "allow": ["B"], "deny": [] }
  }
}
```

**Access to s1:** A OR B (union)

### Deny Always Wins

Explicit denials override all allows:

```jsonnet
{
  "allow": ["admin"],
  "sections": {
    "restricted": {
      "allow": [],
      "deny": ["admin"]  // Denies admin despite process allow
    }
  }
}
```

**Result:** Admin can access all sections EXCEPT "restricted".

## Complex Permission Patterns

### Progressive Restriction

Start broad, then restrict specific sections:

```jsonnet
{
  "allow": ["*"],  // Default: everyone can contribute
  "sections": {
    "sensitive_data": {
      "allow": ["admin", "security-lead"],
      "deny": []
    },
    "financial_info": {
      "allow": ["admin", "finance-lead"],
      "deny": []
    }
  }
}
```

### Role-Based Section Ownership

Clear ownership boundaries:

```jsonnet
{
  "allow": [],  // No default access
  "sections": {
    "frontend": {
      "allow": ["frontend-developer", "ui-designer"],
      "deny": []
    },
    "backend": {
      "allow": ["backend-developer", "api-designer"],
      "deny": []
    },
    "database": {
      "allow": ["dba", "backend-developer"],
      "deny": []
    },
    "infrastructure": {
      "allow": ["devops", "sre"],
      "deny": []
    }
  }
}
```

### Admin Override with Specialist Access

Admin has full access while specialists have targeted access:

```jsonnet
{
  "allow": ["admin"],  // Full access to all sections
  "sections": {
    "code": {
      "allow": ["developer"],  // Also accessible to developers
      "deny": []
    },
    "security": {
      "allow": ["security-engineer"],  // Also accessible to security
      "deny": []
    }
  }
}
```

## BUILD Process Integration

BUILD processes automatically generate permission files with safe defaults:

```jsonnet
{
  "allow": ["pantheon"],  // Conservative default
  "deny": [],
  "sections": {
    "{{section_name}}": {
      "allow": ["pantheon"],
      "deny": []
    }
  }
}
```

### Customizing Generated Permissions

After BUILD scaffolds processes:

1. **Identify Section Owners**: Map sections to responsible agents
2. **Design Additive Access**: Use process-level for broad access, section-level for specialists
3. **Apply Union Thinking**: Remember actors in EITHER process OR section allows get access
4. **Use Explicit Deny**: Restrict access with deny lists since allows are additive
5. **Test Permissions**: Verify access control works as expected

### Common Customization Patterns

**Pattern 1: Broad Process Access + Specialist Sections**
```jsonnet
{
  "allow": ["admin"],              // Admin has access to all sections
  "deny": [],
  "sections": {
    "technical": {
      "allow": ["developer"],      // Developers can ALSO access
      "deny": []                   // Result: admin OR developer
    },
    "business": {
      "allow": ["product-manager"], // PMs can ALSO access
      "deny": []                   // Result: admin OR PM
    }
  }
}
```

**Pattern 2: Section-Only Access**
```jsonnet
{
  "allow": [],  // No broad process access
  "deny": [],
  "sections": {
    "public": {
      "allow": ["*"],  // Everyone
      "deny": []
    },
    "private": {
      "allow": ["team-lead"],  // Only team-lead
      "deny": []
    }
  }
}
```

**Pattern 3: Restrict with Explicit Deny**
```jsonnet
{
  "allow": ["*"],  // Everyone has baseline
  "deny": ["guest"],
  "sections": {
    "sensitive": {
      "allow": ["admin"],  // Admin can access
      "deny": ["*"]        // But deny everyone else
    }
  }
}
```

---

**Cross-References:**
- [Overview](./overview.md) - Security philosophy and model
- [Evaluation Rules](./evaluation-rules.md) - How permissions are evaluated
- [Common Patterns](./common-patterns.md) - Real-world permission examples
