---
doc_id: security-permissions-evaluation
title: "Permission Evaluation Rules"
description: "Complete guide to permission evaluation logic, including precedence rules, the additive union model, and edge case handling."
keywords: [permissions, evaluation, precedence, deny-wins, additive-union, permission-logic]
relevance: "Use this document to understand exactly how the framework evaluates permissions, including the interaction between process-level and section-level rules."
---

# Permission Evaluation Rules

This document explains the complete permission evaluation logic used by the Pantheon Framework to determine whether an actor can execute a process or update a specific section.

## Evaluation Model Overview

Permissions are evaluated using the **"Additive Union with Explicit Deny Wins"** model, following AWS IAM best practices. This model ensures:

- Security by default (deny unless explicitly allowed)
- Predictable behavior (clear precedence rules)
- Flexible access patterns (additive permissions)
- Strong security boundaries (deny always wins)

## Evaluation Order

When an actor attempts to execute a process, the framework evaluates permissions in this order:

### Step 1: Check for Explicit Denials
```
Is actor in sections[X].deny OR process.deny?
  ↓ YES → DENY ACCESS (explicit deny always wins)
  ↓ NO → Continue to Step 2
```

If the actor appears in ANY deny list (process-level or section-level), access is immediately denied. No allow rules can override this.

### Step 2: Create Union of Allows
```
combined_allows = process.allow ∪ sections[X].allow
```

Combine all allow lists that apply:
- Process-level allow list
- Section-level allow list (if checking section access)

This creates an **additive** permission model where actors gain access through multiple paths.

### Step 3: Check Combined Permissions
```
Is actor in combined_allows?
  ↓ YES → GRANT ACCESS
  ↓ NO → Continue to Step 4
```

If the actor appears in the combined allow list, access is granted.

### Step 4: Default Deny
```
DEFAULT → DENY ACCESS
```

If no explicit allow was found, access is denied by default.

## Evaluation Flowchart

```
Request: actor wants to update section X
    ↓
Is actor in sections[X].deny OR process.deny?
    ↓ YES → DENY ACCESS (explicit deny always wins)
    ↓ NO
Create union: combined_allows = process.allow ∪ sections[X].allow
    ↓
Is actor in combined_allows?
    ↓ YES → GRANT ACCESS
    ↓ NO
DEFAULT → DENY ACCESS
```

## Precedence Rules

### Rule 1: Explicit Deny Wins Over Everything

Deny rules have absolute precedence. If an actor is explicitly denied, no allow rule can grant access.

**Example:**
```jsonnet
{
  "allow": ["admin"],
  "sections": {
    "restricted": {
      "allow": ["admin", "security-lead"],
      "deny": ["admin"]  // Denies admin despite allows
    }
  }
}
```

**Result:** Admin can access all sections EXCEPT "restricted" (explicit deny wins).

### Rule 2: Allows Are Additive (Union)

Allow lists from different levels combine through union. Actors gain access if they're in ANY allow list.

**Example:**
```jsonnet
{
  "allow": ["admin"],
  "sections": {
    "technical": {
      "allow": ["developer"],
      "deny": []
    }
  }
}
```

**Result:** Both `admin` AND `developer` can access "technical" (union: admin ∪ developer).

### Rule 3: Default Deny

If no explicit allow or deny applies, access is denied by default.

**Example:**
```jsonnet
{
  "allow": ["admin"],
  "deny": []
}
```

**Result:** Only `admin` has access. All other actors are denied by default.

## Section-Level Evaluation

When evaluating section-level permissions (for UPDATE operations with `--sections` flag):

### Evaluation Steps
1. Check if actor is in `sections[name].deny` → **DENY**
2. Check if actor is in `process.deny` → **DENY**
3. Check if actor is in `sections[name].allow` → **ALLOW**
4. Check if actor is in `process.allow` → **ALLOW**
5. Default → **DENY**

### Example Evaluation

**Permission File:**
```jsonnet
{
  "allow": ["tech-lead"],
  "deny": ["guest"],
  "sections": {
    "code_review": {
      "allow": ["senior-developer"],
      "deny": []
    },
    "deployment": {
      "allow": ["devops"],
      "deny": ["tech-lead"]
    }
  }
}
```

**Evaluation Results:**

| Actor | Section | Evaluation | Result |
|-------|---------|------------|--------|
| tech-lead | code_review | In process.allow | ALLOW |
| senior-developer | code_review | In section.allow | ALLOW |
| junior-developer | code_review | Not in any allow | DENY |
| tech-lead | deployment | In section.deny | DENY |
| devops | deployment | In section.allow | ALLOW |
| guest | any | In process.deny | DENY |

## Wildcard Evaluation

Wildcards (`"*"`) match all actors during evaluation:

### In Allow Lists
```jsonnet
{"allow": ["*"]}
```

Every actor is considered to be in the allow list, subject to deny rules.

### In Deny Lists
```jsonnet
{"deny": ["*"]}
```

Every actor is considered to be in the deny list, which blocks all access.

### Wildcard with Exclusions
```jsonnet
{
  "allow": ["*"],
  "deny": ["guest", "auditor"]
}
```

All actors except `guest` and `auditor` have access.

## Edge Cases and Complex Scenarios

### Case 1: Process Allow + Section Deny (Deny Wins)
```jsonnet
{
  "allow": ["pantheon"],  // Process level: baseline access
  "sections": {
    "restricted": {
      "allow": [],
      "deny": ["pantheon"]  // Section level: explicitly denied
    }
  }
}
```

**Evaluation for `pantheon` on "restricted":**
1. Check denies: `pantheon` in section.deny → **DENY**

**Result:** Pantheon can update all sections EXCEPT "restricted".

### Case 2: Additive Permissions (Union of Allows)
```jsonnet
{
  "allow": ["admin"],  // Process-level access
  "sections": {
    "public": {
      "allow": ["developer"],  // Section adds developer
      "deny": []
    }
  }
}
```

**Evaluation for `developer` on "public":**
1. Check denies: Not in any deny list → Continue
2. Create union: {admin} ∪ {developer} = {admin, developer}
3. Check allows: `developer` in union → **ALLOW**

**Result:** Both `admin` AND `developer` can update "public" section.

### Case 3: Mixed Wildcard with Targeted Deny
```jsonnet
{
  "allow": ["*"],  // Everyone has baseline
  "deny": ["guest"],  // Except guests
  "sections": {
    "critical": {
      "allow": ["admin"],  // Admin can access critical
      "deny": ["*"]  // But deny everyone else
    }
  }
}
```

**Evaluation for `developer` on "critical":**
1. Check denies: `developer` matches `"*"` in section.deny → **DENY**

**Evaluation for `admin` on "critical":**
1. Check denies: `admin` matches `"*"` in section.deny → **DENY**

**Note:** Section deny `"*"` blocks everyone, even those in section allow. This is likely a configuration error. Correct pattern:

```jsonnet
{
  "allow": [],  // No baseline access
  "deny": [],
  "sections": {
    "critical": {
      "allow": ["admin"],
      "deny": []  // Don't deny everyone
    }
  }
}
```

### Case 4: Pure Section-Based Access
```jsonnet
{
  "allow": [],  // No baseline process access
  "deny": [],
  "sections": {
    "team_notes": {
      "allow": ["*"],  // Open to everyone at section level
      "deny": []
    },
    "private": {
      "allow": ["manager"],  // Only manager
      "deny": []
    }
  }
}
```

**Evaluation for `developer` on "team_notes":**
1. Check denies: Not in any deny → Continue
2. Create union: {} ∪ {*} = {*}
3. Check allows: `developer` matches `"*"` → **ALLOW**

**Evaluation for `developer` on "private":**
1. Check denies: Not in any deny → Continue
2. Create union: {} ∪ {manager} = {manager}
3. Check allows: `developer` not in union → Continue
4. Default → **DENY**

## Debugging Permission Denials

When permission is denied, follow this checklist:

### 1. Check Actor Exists
```bash
ls pantheon-teams/<team>/agents/
# Verify actor-name.md exists
```

### 2. Examine Permission File
```bash
cat processes/<process>/permissions.jsonnet
# Check allow/deny lists at both levels
```

### 3. Test Permission Logic

Use the evaluation model mentally:

1. Is actor in section deny? → **DENY**
2. Is actor in process deny? → **DENY**
3. Is actor in section allow? → **ALLOW**
4. Is actor in process allow? → **ALLOW**
5. Default → **DENY**

### 4. Enable Debug Logging
```bash
pantheon --debug execute <process> --actor <actor>
# Shows detailed permission evaluation
```

## Common Evaluation Mistakes

### Mistake 1: Assuming Transitive Allows

**Incorrect Assumption:** If A allows B, and B allows C, then A allows C.

**Reality:** Permissions don't chain. Each level is evaluated independently.

### Mistake 2: Forgetting Deny Precedence

**Incorrect Assumption:** If actor is in both allow and deny, allow wins.

**Reality:** Deny ALWAYS wins, regardless of allow rules.

### Mistake 3: Expecting Override Semantics

**Incorrect Assumption:** Section-level permissions override process-level.

**Reality:** Section-level permissions are ADDITIVE to process-level (union).

### Mistake 4: Wildcard Deny Blocks Everything

**Incorrect Pattern:**
```jsonnet
{
  "sections": {
    "sensitive": {
      "allow": ["admin"],
      "deny": ["*"]  // This blocks admin too!
    }
  }
}
```

**Correct Pattern:**
```jsonnet
{
  "allow": [],  // Start with no access
  "sections": {
    "sensitive": {
      "allow": ["admin"],  // Only admin gets access
      "deny": []
    }
  }
}
```

---

**Cross-References:**
- [Overview](./overview.md) - Security philosophy and model
- [Permission System](./permission-system.md) - File structure and patterns
- [Common Patterns](./common-patterns.md) - Real-world examples
