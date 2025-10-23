---
doc_id: security-permissions-patterns
title: "Common Permission Patterns"
description: "Real-world permission patterns and best practices for implementing secure, collaborative workflows with proper access control."
keywords: [permissions, patterns, best-practices, access-control, collaboration, role-based]
relevance: "Use this document to find proven permission patterns for common scenarios like single-owner processes, admin oversight, public collaboration, and role-based access."
---

# Common Permission Patterns

This document provides proven permission patterns for common access control scenarios, demonstrating how to implement secure, collaborative workflows.

## Pattern 1: Single-Owner Process

**Use Case:** Simple processes with one responsible actor.

### Basic Single Owner
```jsonnet
{
  "allow": ["tech-lead"],
  "deny": []
}
```

**Access:** Only `tech-lead` can execute the process.

### Single Owner with Backup
```jsonnet
{
  "allow": ["tech-lead", "senior-developer"],
  "deny": []
}
```

**Access:** Primary owner (`tech-lead`) and backup (`senior-developer`) can execute.

### Single Owner with Exclusions
```jsonnet
{
  "allow": ["developer"],
  "deny": ["junior-developer", "intern"]
}
```

**Access:** All actors named `developer` except explicitly excluded ones.

## Pattern 2: Admin + Specialist (Additive Permissions)

**Use Case:** Admin oversight with specialist access. Permissions are additive.

### Basic Admin Oversight
```jsonnet
{
  "allow": ["pantheon"],  // Admin has baseline access to all sections
  "sections": {
    "code_review": {
      "allow": ["senior-developer", "code-reviewer"],  // Adds to admin
      "deny": []
    },
    "security_review": {
      "allow": ["security-engineer"],  // Adds to admin
      "deny": []
    }
  }
}
```

**Results:**
- "code_review": `pantheon` OR `senior-developer` OR `code-reviewer` (union)
- "security_review": `pantheon` OR `security-engineer` (union)
- Other sections: `pantheon` only

### Admin with Distributed Ownership
```jsonnet
{
  "allow": ["admin"],
  "deny": [],
  "sections": {
    "technical": {
      "allow": ["developer"],  // Developers can ALSO access
      "deny": []  // Result: admin OR developer
    },
    "business": {
      "allow": ["product-manager"],  // PMs can ALSO access
      "deny": []  // Result: admin OR PM
    },
    "deployment": {
      "allow": ["devops"],  // DevOps can ALSO access
      "deny": []  // Result: admin OR devops
    }
  }
}
```

**Pattern:** Admin retains full access while specialists own their domains.

## Pattern 3: Public Collaboration with Restrictions

**Use Case:** Open collaboration with protected areas.

### Open with Sensitive Sections
```jsonnet
{
  "allow": ["*"],  // Everyone can participate
  "deny": ["external-auditor"],  // Except auditors
  "sections": {
    "final_decisions": {
      "allow": ["tech-lead", "product-manager"],  // Decision makers only
      "deny": []
    },
    "budget": {
      "allow": ["finance-lead"],  // Finance only
      "deny": []
    }
  }
}
```

**Results:**
- General sections: Everyone except `external-auditor`
- "final_decisions": `tech-lead` OR `product-manager` OR anyone (too permissive!)

**Problem:** Process-level wildcard allows everyone into all sections. Better pattern:

```jsonnet
{
  "allow": [],  // No baseline access
  "deny": [],
  "sections": {
    "discussion": {
      "allow": ["*"],  // Open collaboration
      "deny": ["external-auditor"]
    },
    "final_decisions": {
      "allow": ["tech-lead", "product-manager"],  // Restricted
      "deny": []
    }
  }
}
```

### Progressive Restriction
```jsonnet
{
  "allow": ["*"],  // Default: everyone can contribute
  "deny": [],
  "sections": {
    "sensitive_data": {
      "allow": ["admin", "security-lead"],  // Adds restricted access
      "deny": []  // Result: admin OR security-lead OR everyone (!)
    }
  }
}
```

**Problem:** Wildcard at process level grants access to all sections. Correct pattern:

```jsonnet
{
  "allow": [],  // Start with no baseline
  "deny": [],
  "sections": {
    "public": {
      "allow": ["*"],  // Everyone
      "deny": []
    },
    "sensitive_data": {
      "allow": ["admin", "security-lead"],  // Only these actors
      "deny": []
    }
  }
}
```

## Pattern 4: Role-Based Section Ownership

**Use Case:** Clear ownership boundaries with no overlap.

### Specialist Domains
```jsonnet
{
  "allow": [],  // No default access
  "deny": [],
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

**Pattern:** Each section has dedicated specialists with no baseline access.

### Multi-Stage Workflow
```jsonnet
{
  "allow": [],
  "deny": [],
  "sections": {
    "requirements": {
      "allow": ["product-manager", "business-analyst"],
      "deny": []
    },
    "design": {
      "allow": ["architect", "tech-lead"],
      "deny": []
    },
    "implementation": {
      "allow": ["developer", "senior-developer"],
      "deny": []
    },
    "testing": {
      "allow": ["qa-engineer"],
      "deny": []
    },
    "deployment": {
      "allow": ["devops", "release-manager"],
      "deny": []
    }
  }
}
```

**Pattern:** Workflow stages map to different specialists.

## Pattern 5: Separation of Duties

**Use Case:** Prevent conflicts of interest through access control.

### No Self-Review
```jsonnet
{
  "allow": ["developer"],  // Can implement
  "sections": {
    "code_review": {
      "allow": ["code-reviewer", "tech-lead"],  // Cannot self-review
      "deny": ["developer"]
    }
  }
}
```

**Result:** Developers can implement but cannot review their own work.

### Financial Controls
```jsonnet
{
  "allow": [],
  "deny": [],
  "sections": {
    "requisition": {
      "allow": ["project-manager"],  // Can request
      "deny": []
    },
    "approval": {
      "allow": ["finance-director"],  // Can approve
      "deny": ["project-manager"]  // Cannot self-approve
    },
    "payment": {
      "allow": ["accounting"],  // Can execute
      "deny": ["project-manager", "finance-director"]
    }
  }
}
```

**Pattern:** Three-way separation prevents single-actor fraud.

## Pattern 6: Graduated Access

**Use Case:** Access increases with seniority or trust level.

### Junior/Senior Developer Split
```jsonnet
{
  "allow": ["senior-developer"],
  "sections": {
    "simple_features": {
      "allow": ["junior-developer"],  // Adds junior access
      "deny": []  // Result: senior OR junior
    },
    "core_architecture": {
      "allow": [],  // Only senior (from process level)
      "deny": []
    }
  }
}
```

**Results:**
- "simple_features": `senior-developer` OR `junior-developer`
- "core_architecture": `senior-developer` only

### Trust-Based Access
```jsonnet
{
  "allow": ["trusted-contributor"],
  "sections": {
    "documentation": {
      "allow": ["*"],  // Everyone can document
      "deny": []  // Result: everyone
    },
    "configuration": {
      "allow": [],  // Only trusted (from process level)
      "deny": []
    },
    "security": {
      "allow": ["security-lead"],  // Adds security-lead
      "deny": []  // Result: trusted OR security-lead
    }
  }
}
```

## Pattern 7: Emergency Access

**Use Case:** Break-glass access for emergencies.

### Emergency Override
```jsonnet
{
  "allow": ["developer"],
  "sections": {
    "production_config": {
      "allow": ["emergency-admin"],  // Can access in emergency
      "deny": []  // Result: developer OR emergency-admin
    }
  }
}
```

### Audit-Required Access
```jsonnet
{
  "allow": ["admin"],
  "deny": [],
  "sections": {
    "sensitive_logs": {
      "allow": ["auditor"],  // Auditors can access
      "deny": []  // Result: admin OR auditor
    }
  }
}
```

**Note:** Combine with audit logging to track emergency access usage.

## Pattern 8: Temporary Access

**Use Case:** Grant access during specific project phases.

### Project-Phase Access
```jsonnet
{
  "allow": ["tech-lead"],
  "sections": {
    "migration_plan": {
      "allow": ["migration-specialist"],  // Active during migration
      "deny": []
    }
  }
}
```

**Practice:** Update permissions when project phases change. Version control tracks these changes.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Wildcard Deny with Specific Allow
```jsonnet
{
  "allow": [],
  "sections": {
    "sensitive": {
      "allow": ["admin"],
      "deny": ["*"]  // ❌ This blocks admin too!
    }
  }
}
```

**Problem:** Deny `"*"` matches everyone, including `admin`.

**Correct:**
```jsonnet
{
  "allow": [],
  "sections": {
    "sensitive": {
      "allow": ["admin"],
      "deny": []  // ✓ Only admin gets access
    }
  }
}
```

### Anti-Pattern 2: Redundant Denials
```jsonnet
{
  "allow": ["tech-lead"],
  "deny": ["junior-developer"]  // ❌ Unnecessary
}
```

**Problem:** `junior-developer` is already denied by default (not in allow list).

**Correct:**
```jsonnet
{
  "allow": ["tech-lead"],
  "deny": []  // ✓ Simpler and equivalent
}
```

Use explicit denials only when:
- Removing access from wildcards
- Documenting exclusion intent
- Overriding section-level allows

### Anti-Pattern 3: Process-Level Wildcard with "Private" Sections
```jsonnet
{
  "allow": ["*"],  // ❌ Grants baseline access to all
  "sections": {
    "private": {
      "allow": ["admin"],  // Ineffective!
      "deny": []  // Result: admin OR everyone
    }
  }
}
```

**Problem:** Process-level wildcard makes sections public.

**Correct:**
```jsonnet
{
  "allow": [],  // ✓ No baseline access
  "sections": {
    "public": {
      "allow": ["*"],
      "deny": []
    },
    "private": {
      "allow": ["admin"],
      "deny": []
    }
  }
}
```

## Best Practices

### 1. Start Restrictive
Begin with minimal permissions and expand as needed:
```jsonnet
{
  "allow": ["admin"],
  "deny": []
}
```

Expand to specialists later based on actual needs.

### 2. Document Permission Rationale
```jsonnet
{
  // Only senior engineers can modify production configs
  // to prevent accidental breakage. Junior engineers
  // can request changes through tickets.
  "allow": ["senior-engineer", "tech-lead"],
  "deny": []
}
```

### 3. Use Descriptive Actor Names
```jsonnet
// ❌ Unclear
"allow": ["user1", "user2"]

// ✓ Clear
"allow": ["backend-specialist", "api-designer"]
```

### 4. Review Permissions Regularly
- Remove deprecated agents from allow lists
- Update access as roles change
- Audit sensitive section access
- Check for unused wildcards

### 5. Test Permission Changes
```bash
# Before deploying permission changes:
pantheon execute update-config --actor developer --from-file test.json
# Verify expected access/denial
```

---

**Cross-References:**
- [Overview](./overview.md) - Security philosophy and model
- [Permission System](./permission-system.md) - File structure details
- [Evaluation Rules](./evaluation-rules.md) - How permissions are evaluated
