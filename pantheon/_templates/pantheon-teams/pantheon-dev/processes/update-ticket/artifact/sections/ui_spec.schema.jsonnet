{
  "type": "object",
  "required": [
    "ascii_wireframe",
    "layout_notes",
    "navigation_flow",
    "state_transitions",
    "decision_title",
    "rationale",
    "alternatives"
  ],
  "properties": {
    "ascii_wireframe": {
      "authoring_guidance": "Use ASCII box-drawing characters (|, -, +, etc.) to create clear visual structure. Show component hierarchy through indentation and nesting. Label all interactive elements. Aim for clarity over artistic detail. Target 20-50 lines for simple layouts, 50-100 for complex ones.",
      "description_for_schema": "ASCII art representation of the user interface layout. Use box-drawing characters, brackets, and text to show component hierarchy and spatial relationships.",
      "purpose": "Provides token-efficient visual representation of UI structure using ASCII characters, serving as the single source of truth for layout and spatial relationships.",
      "type": "string"
    },
    "layout_notes": {
      "authoring_guidance": "Provide 3-6 discrete notes. Focus on behavior not obvious from the ASCII (responsive breakpoints, hidden/shown states, animations). Each note should be a single clear point.",
      "description_for_schema": "List of notes explaining layout behavior, responsive considerations, or aspects not clearly shown in the ASCII representation.",
      "purpose": "Documents key aspects of the layout that are difficult to express in ASCII alone, such as responsive behavior or animation states.",
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "navigation_flow": {
      "authoring_guidance": "Target 15-40 lines. Use arrows to connect states/screens. Label each transition with the action that triggers it (e.g., 'Click Login', 'Submit Form'). Show all possible paths including error states.",
      "description_for_schema": "ASCII diagram showing how users navigate between screens, views, or states. Use arrows (->, <-) and labels to show transitions.",
      "purpose": "Shows how users move between screens or views using ASCII arrows and labels, establishing the interaction model that drives implementation.",
      "type": "string"
    },
    "state_transitions": {
      "authoring_guidance": "Include 2-6 transitions covering loading, error, and success states. Each transition should specify what triggers it and what changes visually.",
      "description_for_schema": "List of state transitions within views, each specifying the starting state, ending state, trigger condition, and visual change.",
      "purpose": "Documents state changes within a single view, such as loading states, error displays, or progressive disclosure behavior.",
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from_state", "to_state", "trigger", "visual_change"],
        "properties": {
          "from_state": {
            "type": "string",
            "description_for_schema": "The initial state before the transition (e.g., 'idle', 'loading', 'form_visible')."
          },
          "to_state": {
            "type": "string",
            "description_for_schema": "The resulting state after the transition (e.g., 'loading', 'success', 'error')."
          },
          "trigger": {
            "type": "string",
            "description_for_schema": "The action or condition that causes this transition (e.g., 'Click Submit', 'API returns 200', 'Timeout after 30s')."
          },
          "visual_change": {
            "type": "string",
            "description_for_schema": "What changes visually when this transition occurs (e.g., 'Show spinner overlay', 'Display success toast', 'Highlight error fields')."
          }
        }
      }
    },
    "decision_title": {
      "authoring_guidance": "Keep under 100 characters. Focus on what was decided, not why. The rationale field captures the 'why'.",
      "description_for_schema": "Brief title summarizing the design decision (e.g., 'Place navigation at top instead of sidebar', 'Use modal for confirmation instead of inline').",
      "purpose": "Provides concise summary of the design decision for quick scanning and reference.",
      "type": "string"
    },
    "rationale": {
      "authoring_guidance": "Target 75-150 words. Explain the reasoning clearly. Reference specific user needs from brainstorming if applicable. Include any constraints that influenced the decision.",
      "description_for_schema": "Explanation of why this design decision was made. Include user needs, technical constraints, or usability considerations that drove the choice.",
      "purpose": "Explains why this design choice was made, preserving context for future changes or questions.",
      "type": "string"
    },
    "alternatives": {
      "authoring_guidance": "List 1-3 alternatives. Each should name the approach and explain why it was rejected. This helps future designers understand the full exploration.",
      "description_for_schema": "List of alternative approaches that were considered, each with the approach name and reason for rejection.",
      "purpose": "Documents approaches that were considered but rejected, helping future designers understand what was explored and why other paths weren't chosen.",
      "type": "array",
      "items": {
        "type": "object",
        "required": ["approach", "rejection_reason"],
        "properties": {
          "approach": {
            "type": "string",
            "description_for_schema": "Name or brief description of the alternative approach (e.g., 'Sidebar navigation', 'Inline editing')."
          },
          "rejection_reason": {
            "type": "string",
            "description_for_schema": "Why this approach was not chosen (e.g., 'Takes too much horizontal space on mobile', 'Adds complexity without clear benefit')."
          }
        }
      }
    }
  }
}