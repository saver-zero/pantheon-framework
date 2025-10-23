{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "process_name": {
      "type": "string",
      "description_for_schema": "The kebab-case name of the process this routine is for (e.g., 'create-new-ticket', 'review-plan').",
      "purpose": "The name of the process for which this routine is being created. This will be displayed as the main heading of the routine."
    },
    "process_type": {
      "type": "string",
      "enum": ["create", "get", "update"],
      "description_for_schema": "The type of process routine to generate.",
      "purpose": "Determines which template to use for the routine."
    },
    "artifact_name": {
      "type": "string",
      "description_for_schema": "The canonical name of the artifact this routine targets (e.g., 'team-blueprint').",
      "authoring_guidance": "Only required for update routines. Provide the artifact name in kebab-case so downstream templates can reference it consistently.",
      "purpose": "Supplies the artifact identifier used by update workflows to reference the resource being modified."
    },
    "objective": {
      "type": "string",
      "description_for_schema": "A clear, concise statement of what this routine accomplishes. Should be specific enough to guide execution but general enough to be reusable.",
      "authoring_guidance": "Write a single sentence that captures the essential purpose. Focus on the outcome, not the process. Aim for 10-25 words.",
      "purpose": "Defines the clear goal and expected outcome of the routine to guide agent understanding and execution. This serves as the north star for the entire workflow, ensuring every step contributes to achieving this stated purpose."
    },
    "steps": {
      "type": "array",
      "minItems": 1,
      "description_for_schema": "Ordered list of steps following the six node types pattern: node, branch, branchstartnode, branchnode, branchfinishnode, and finish.",
      "authoring_guidance": "Your task is to define only the custom, intermediate steps of the routine. Think of your role as filling in the middle chapters of a book; the first and last chapters are already written for you by a template.\n\nFocus exclusively on the core logic of the process. Your steps will be injected between a standard setup (Get Schema, Get Context) and a standard wrap-up (Quality Review, Get tempfile, Save JSON, Execute Process).\n\nYou are free to use `branchfinishnode` to terminate any conditional path within your logic. However, you MUST NOT provide the final, top-level `finish` node. The template will always add the final `finish` step to the routine.",
      "items": {
        "anyOf": [
          { "$ref": "#/$defs/node" },
          { "$ref": "#/$defs/branch" },
          { "$ref": "#/$defs/finish" }
        ]
      },
      "purpose": "Contains the structured sequence of workflow steps that guide the agent through the routine."
    }
  },
  "required": ["process_name", "process_type", "objective", "steps"],
  "allOf": [
    {
      "if": {
        "properties": {
          "process_type": { "const": "update" }
        }
      },
      "then": {
        "required": ["artifact_name"]
      }
    }
  ],
  "$defs": {
    "node": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "node_type": { "const": "node" },
        "name": {
          "type": "string",
          "description_for_schema": "A concise, action-oriented name (e.g., 'Get schema').",
          "purpose": "Label displayed in the rendered routine so the agent immediately understands the intent of the step."
        },
        "description": {
          "type": "string",
          "description_for_schema": "Exactly one instruction that tells the agent what to do in this step.",
          "authoring_guidance": "Write a single imperative sentence. Do not chain multiple commands or include follow-up actions.",
          "purpose": "Guides the agent's cognitive or execution focus for this step without overloading it."
        },
        "tool": {
          "type": "string",
          "description_for_schema": "If needed, the Pantheon CLI command to execute.",
          "authoring_guidance": "Only include when the step genuinely requires tool execution.",
          "purpose": "Provides the exact command to run when the step requires tool execution."
        }
      },
      "required": ["node_type", "name", "description"],
      "description_for_schema": "A standard sequential step."
    },
    "branch": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "node_type": { "const": "branch" },
        "name": {
          "type": "string",
          "description_for_schema": "A concise name for the branch decision point.",
          "purpose": "Summarises the decision the agent is about to make."
        },
        "description": {
          "type": "string",
          "description_for_schema": "Short context describing the decision criterion.",
          "authoring_guidance": "State the condition being checked in one sentence without prescribing actions.",
          "purpose": "Provides the context the agent should consider when evaluating the branch."
        },
        "paths": {
          "type": "array",
          "minItems": 2,
          "description_for_schema": "Conditional paths available from this decision point. Each path begins with one branchstartnode followed by zero or more additional branch steps.",
          "items": { "$ref": "#/$defs/branch_path" },
          "purpose": "Encodes the alternative execution tracks based on the decision outcome."
        }
      },
      "required": ["node_type", "name", "description", "paths"],
      "description_for_schema": "A decision point with multiple conditional paths."
    },
    "branch_path": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "start": { "$ref": "#/$defs/branchstartnode" },
        "steps": {
          "type": "array",
          "items": {
            "anyOf": [
              { "$ref": "#/$defs/branchnode" },
              { "$ref": "#/$defs/branchfinishnode" }
            ]
          },
          "description_for_schema": "Follow-on steps for this branch path. May include additional actions and must terminate with a branchfinishnode when the path ends.",
          "purpose": "Ensures each branch path performs its required actions after the condition is established."
        }
      },
      "required": ["start"],
      "description_for_schema": "Structure of a single branch path, enforcing one branchstartnode per path."
    },
    "branchstartnode": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "node_type": { "const": "branchstartnode" },
        "name": {
          "type": "string",
          "description_for_schema": "A concise name for this branch path (e.g., 'Continue').",
          "purpose": "Communicates the result of the condition in the rendered routine."
        },
        "condition": {
          "type": "string",
          "description_for_schema": "The condition for entering this branch path (e.g., 'ticket id was provided').",
          "authoring_guidance": "State the condition succinctly. Avoid additional actions or follow-on guidance here.",
          "purpose": "States the branch predicate once so it is not repeated in subsequent steps."
        },
        "action": {
          "type": "string",
          "description_for_schema": "The first action to perform when the condition is met.",
          "authoring_guidance": "Write a single imperative instruction that kicks off the branch path.",
          "purpose": "Sets the initial activity for the branch after the condition check."
        },
        "tool": {
          "type": "string",
          "description_for_schema": "If needed, the Pantheon CLI command to execute.",
          "authoring_guidance": "Only include when the branch start must immediately call a tool.",
          "purpose": "Optional command that should run immediately after the condition is satisfied."
        }
      },
      "required": ["node_type", "name", "condition", "action"],
      "description_for_schema": "The required first step inside each branch path that captures the condition and initial action."
    },
    "branchnode": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "node_type": { "const": "branchnode" },
        "name": {
          "type": "string",
          "description_for_schema": "A concise name for this branch step (e.g., 'Collect context').",
          "purpose": "Explains the action or reasoning the agent should perform at this point in the branch."
        },
        "description": {
          "type": "string",
          "description_for_schema": "Exactly one instruction executed after the branchstartnode condition is met.",
          "authoring_guidance": "Keep to a single imperative sentence focused on the immediate action.",
          "purpose": "Provides focused guidance for the follow-on action."
        },
        "tool": {
          "type": "string",
          "description_for_schema": "If needed, the Pantheon CLI command to execute.",
          "authoring_guidance": "Only include when this step must call a tool.",
          "purpose": "Optional command associated with this step."
        }
      },
      "required": ["node_type", "name", "description"],
      "description_for_schema": "A follow-on action inside a branch path that continues the workflow."
    },
    "branchfinishnode": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "node_type": { "const": "branchfinishnode" },
        "name": {
          "type": "string",
          "description_for_schema": "A name indicating workflow completion for this path.",
          "purpose": "Signals to the agent that this branch path terminates here."
        },
        "description": {
          "type": "string",
          "description_for_schema": "Single instruction that finalizes the branch path.",
          "authoring_guidance": "Use this node ONLY to terminate a branch that represents an early exit from the routine (e.g., due to invalid input, missing prerequisites, or if no action is needed). Do NOT use this for a 'successful' path where the core work is completed. A successful path should simply continue, allowing the routine to proceed to the standard wrap-up steps.",
          "purpose": "Explains the concluding activity the agent must perform on this branch."
        },
        "tool": {
          "type": "string",
          "description_for_schema": "If needed, the Pantheon CLI command to execute.",
          "authoring_guidance": "Only include when the terminating step requires a tool call.",
          "purpose": "Optional command tied to the terminating action."
        }
      },
      "required": ["node_type", "name", "description"],
      "description_for_schema": "A final action inside a branch path that terminates the workflow."
    },
    "finish": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "node_type": { "const": "finish" },
        "name": {
          "type": "string",
          "description_for_schema": "A name indicating workflow completion.",
          "purpose": "Tells the agent the workflow ends at this step."
        },
        "description": {
          "type": "string",
          "description_for_schema": "Single instruction that completes the overall routine.",
          "authoring_guidance": "Give one definitive action that closes out the workflow.",
          "purpose": "Clarifies the closing task prior to termination."
        },
        "tool": {
          "type": "string",
          "description_for_schema": "If needed, the final Pantheon CLI command to execute.",
          "authoring_guidance": "Only include when the terminal step requires a tool call.",
          "purpose": "Optional command executed as the final action."
        }
      },
      "required": ["node_type", "name", "description"],
      "description_for_schema": "The final step in any path that terminates the workflow."
    }
  }
}
