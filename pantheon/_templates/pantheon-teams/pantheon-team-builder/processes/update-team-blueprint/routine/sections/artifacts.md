Step {{ _current_step_index.num }}. **Identify Artifacts:** Review the reference workflow and list every deliverable it explicitly names or clearly implies. Consolidate overlapping deliverables (e.g., merge two different docs into a single plan). Discard any artifact ideas that cannot be traced to the source.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }} (branch). **Apply User-Centric Naming for Artifacts:** Determine the appropriate naming approach based on the team's domain.
- Branch {{ _current_step_index.num }}-1 Step 1. **Non-technical team:** If this team serves non-technical users, then name artifacts based on what users are creating or what outcome they're achieving. Think: "What am I making?" rather than "What data structure is this?"
- Branch {{ _current_step_index.num }}-2 Step 1. **Technical team:** If this team is for technical/software work, then technical artifact names are clear and appropriate.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Define Purposes:** For each artifact you kept, write its purpose and record a `source_reference` quoting or summarizing the part of the workflow that justifies it. If you cannot cite the source, remove the artifact or document the idea as operator guidance instead of keeping it here.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Design Sections:** For each artifact, list only the sections that operators or the primary implementation LLM can populate manually. Avoid real-time telemetry or anything Pantheon cannot store. Provide concise descriptions for each section and ensure each section delivers unique value -- remove any that duplicate information available elsewhere.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Plan Section Sequence:** Describe the practical order in which sections should be created, reviewed, or updated so the primary implementation LLM has a clear workflow. Reference the section names, specify the action (create, review, update), and briefly explain why the step happens at that point.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Select Pantheon Operations:** Choose the CREATE/GET/UPDATE verbs that materially help operators. Omit any verb that would be redundant or unenforceable.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Capture External Inputs and Manual Actions:** Note any external data that must be ingested via Pantheon artifacts and list the manual operator steps required. Confirm these steps align with the workflow and do not imply automated monitoring.
{% set _current_step_index.num = _current_step_index.num + 1 %}