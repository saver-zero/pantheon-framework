---
doc_id: security-permissions-overview
title: "Security & Permissions Overview"
description: "Overview of the Pantheon Framework's actor-based permission system, security philosophy, and two-tier permission model."
keywords: [security, permissions, actor-based, access-control, authorization, security-philosophy]
relevance: "Use this document to understand the foundational security principles and permission architecture that controls access to processes and artifacts."
---

# Security & Permissions Overview

The Pantheon Framework implements a comprehensive actor-based permission system that controls access to processes and artifact sections. This system ensures secure, collaborative workflows while maintaining clear boundaries between different agent roles.

## Security Philosophy

The framework's security model is built on four core principles:

### Secure by Default
Access is denied unless explicitly granted. Every process must have a `permissions.jsonnet` file that defines who can execute it. Missing permission files result in access denial, preventing accidental exposure.

### Explicit Permissions
All access must be defined in `permissions.jsonnet` files. There are no implicit permissions based on agent names, roles, or other heuristics. This makes security decisions visible and auditable.

### Least Privilege
Grant minimum necessary access for each actor. Use process-level permissions for broad access and section-level permissions for fine-grained control. Start restrictive and expand as needed rather than starting permissive.

### Auditability
Clear permission trails for compliance and debugging. All permission decisions are:
- Defined in version-controlled files
- Evaluated using consistent, documented rules
- Logged in audit trails (when enabled)
- Traceable to specific actor actions

## Two-Tier Permission Model

The framework provides two complementary levels of access control:

### 1. Process-Level Permissions
Control access to entire processes, regardless of operation type (CREATE, UPDATE, GET).

**Use Cases:**
- General access control for standard processes
- Restricting dangerous or administrative operations
- Defining baseline permissions for all sections

**Example:**
```jsonnet
{
  "allow": ["tech-lead", "senior-developer"],
  "deny": ["deprecated-agent"]
}
```

### 2. Section-Level Permissions
Fine-grained control over document sections within UPDATE operations. Enables collaborative workflows where different specialists own different parts of an artifact.

**Use Cases:**
- Multi-specialist collaboration on complex documents
- Progressive access as artifacts move through workflow stages
- Restricting sensitive sections while keeping others open

**Example:**
```jsonnet
{
  "allow": ["pantheon"],  // Admin has full access
  "sections": {
    "technical_design": {
      "allow": ["architect", "tech-lead"],
      "deny": []
    },
    "security_review": {
      "allow": ["security-engineer"],
      "deny": []
    }
  }
}
```

## Actor-Based Model

Every command must identify the actor performing the action using the `--actor` flag:

```bash
pantheon execute update-plan --actor backend-engineer --from-file plan.json
```

### Actor Validation
1. **Actor Existence**: Framework verifies the actor corresponds to an agent file in `agents/`
2. **Permission Check**: Evaluates `permissions.jsonnet` to determine access
3. **Execution**: Only proceeds if all permissions pass

### Actor Identification Benefits
- **Accountability**: Every action is traceable to a specific agent
- **Permission Enforcement**: Enables role-based access control
- **Audit Trails**: Complete history of who did what and when
- **Security Boundaries**: Prevents unauthorized access to sensitive operations

## Permission File Structure

Every process **must** include a `permissions.jsonnet` file at the process root:

```
processes/<process-name>/
├── routine.md
├── permissions.jsonnet    # Required
├── schema.jsonnet
└── artifact/
```

### Basic Structure
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

## Permission Evaluation Overview

Permissions are evaluated using the **"Additive Union with Explicit Deny Wins"** model, following AWS IAM best practices:

1. **ANY DENY wins** → Check both process-level and section-level deny lists first
2. **UNION of ALLOWs** → Combine process-level and section-level allow lists
3. **Check combined permissions** → Actor must be in the unified allow list
4. **Default** → Access denied

This ensures that:
- Explicit denials always block access
- Permissions are additive across levels
- Default-deny provides security by default
- Complex access patterns can be expressed clearly

## Integration with Development Workflow

### CLI Integration
The CLI enforces permissions before process execution:

```bash
# Success: actor has permission
pantheon execute update-plan --actor tech-lead --sections implementation

# Failure: actor lacks section permission
pantheon execute update-plan --actor junior-dev --sections sensitive_config
# Error: Actor 'junior-dev' lacks permission for section 'sensitive_config'
```

### Permission Error Messages
All permission errors are **non-recoverable** and require immediate termination:

- **Process denied**: `Actor 'X' lacks permission for process 'Y'. This is a non-recoverable error. You MUST STOP.`
- **Explicit deny**: `Actor 'X' is explicitly denied access to process 'Y'. This is a non-recoverable error. You MUST STOP.`
- **Section denied**: `Actor 'X' lacks permission for section 'Z' in process 'Y'. This is a non-recoverable error. You MUST STOP.`

### BUILD Process Integration

BUILD processes automatically generate `permissions.jsonnet` files for all created processes with safe defaults:

```jsonnet
{
  "allow": ["pantheon"],  // Safe default: admin access only
  "deny": [],
  "sections": {
    "{{section_name}}": {
      "allow": ["pantheon"],
      "deny": []
    }
  }
}
```

After BUILD generates processes, review and customize permissions based on your team's access control requirements.

## Security Best Practices

### 1. Start Restrictive
Begin with minimal permissions and expand as needed:
```jsonnet
{
  "allow": ["admin"],  // Start with admin-only access
  "deny": []
}
```

### 2. Use Explicit Deny for Exclusions
When using wildcards, explicitly deny specific actors:
```jsonnet
{
  "allow": ["*"],
  "deny": ["guest", "external-auditor"]
}
```

### 3. Document Permission Rationale
Add comments explaining permission decisions:
```jsonnet
{
  // Only senior engineers can update production configs
  "allow": ["senior-developer", "tech-lead"],
  "deny": []
}
```

### 4. Regular Security Audits
Periodically review permissions to ensure they remain appropriate:
- Remove permissions for deprecated agents
- Verify sensitive sections have restricted access
- Check for overly permissive wildcards

### 5. Separation of Duties
Use section-level permissions to enforce separation:
```jsonnet
{
  "sections": {
    "code_implementation": {
      "allow": ["developer"],
      "deny": []
    },
    "security_review": {
      "allow": ["security-engineer"],  // Different actor
      "deny": ["developer"]  // Prevent self-review
    }
  }
}
```

---

**Cross-References:**
- [Permission System](./permission-system.md) - Detailed permission file structure
- [Evaluation Rules](./evaluation-rules.md) - Complete evaluation model
- [Common Patterns](./common-patterns.md) - Real-world permission patterns
