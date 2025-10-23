{% if pantheon_active_profile.read_documentation %}

Step {{ _current_step_index.num }}. **Get the architecture guide:** Use `pantheon execute get-architecture-guide --sections high-level-overview,core-principles,implementation-patterns --actor <your_agent_name>` to get the the relevant sections of the architecture guide.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }} (branch). **Check architecture guide:** Perform a branch condition check. Check if architecture guide exists with content.:
  - Branch {{ _current_step_index.num }}-1 Step 1. **Architecture guide exists:** If architecture guide exists with content, then read the content and continue to the next step.
  - Branch {{ _current_step_index.num }}-2 Step 1. **Architecture guide does not exist:** If architecture guide does not exist or has empty content, then check for additional documentation. Use `pantheon get team-data --key path.docs --actor <your_agent_name>` to get the documentation directory.
  - Branch {{ _current_step_index.num }}-2 Step 2. **Understand the Documentation Structure:** Leverage any README or INDEX files and the directory structure to understand the overall documentation structure.
  - Branch {{ _current_step_index.num }}-2 Step 3. **Understand architecture and design principles:** Identify and read documentation related to architecture pattern or design principles.
{% set _current_step_index.num = _current_step_index.num + 1 %}

{% endif %}
Step {{ _current_step_index.num }}. **Retrieve baseline commit:** Get the baseline commit information to establish the diff starting point. Use the baseline_commit section to identify the commit hash and branch for comparison.. Use `pantheon execute get-ticket --id <ticket_id> --sections baseline_commit --actor <your_agent_name>`
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Identify changed files:** Get the list of files modified and the lines changed since the baseline commit to understand the scope of changes. Use `git diff <baseline_commit_hash>...HEAD --numstat`
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }} (branch). **Assess change scope:** Perform a branch condition check. Calculate total lines changed (sum of insertions + deletions from --numstat output). Determine if the scope requires batched review to maintain systematic review quality.:
  - Branch {{ _current_step_index.num }}-1 Step 1. **Small changeset:** If total lines changed is fewer than 500 lines AND fewer than 10 files, then plan to review all changes in a single comprehensive pass across all four pillars.
  - Branch {{ _current_step_index.num }}-2 Step 1. **Large changeset:** If total lines changed is 500 or more, OR 10 or more files changed, OR changes are architecturally significant, then begin planning the review batches, starting with core source files.
  - Branch {{ _current_step_index.num }}-2 Step 2. **Plan core source file batches:** Create logical batches for core source files. Your primary goal is to maximize logical cohesion by grouping related files, classes, and functions. If a file is too large, split it at function or class boundaries. To ensure a focused review and prevent context overload, keep batches under 500 lines.
  - Branch {{ _current_step_index.num }}-2 Step 3. **Plan test file batches:** Next, create logical batches for test files. Group tests by feature or component, keeping batches under 500 lines to maintain focus without breaking up a logical test suite.
  - Branch {{ _current_step_index.num }}-2 Step 4. **Plan remaining file batches:** Finally, group all remaining files, such as configuration, documentation, and diagrams, into one or more small, logical batches.
{% set _current_step_index.num = _current_step_index.num + 1 %}

{% set _batch_review_step = _current_step_index.num %}
Step {{ _current_step_index.num }}. **Get diff for batch:** Retrieve the code changes for the current batch of files to analyze across all review pillars. Use `git diff <baseline_commit_hash>...HEAD -- <file_paths_for_this_batch>`
{% set _current_step_index.num = _current_step_index.num + 1 %}

{% if pantheon_active_profile.read_documentation %}
Step {{ _current_step_index.num }}. **Review architecture:** Validate the code changes against the project's documented architecture patterns, design principles, and coding standards identified earlier. Check for adherence to established patterns, consistency with architectural decisions, violations of documented conventions, and deviations from project structure. Consider both explicit violations and subtle inconsistencies. Above all, it's of utmost importance to be pragmatic over being perfect, ensuring there is no over architecting (again, YAGNI).
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% else %}
Step {{ _current_step_index.num }}. **Review architecture:** Validate the code changes against industry best practices and software engineering principles - Separation of Concerns, low coupling with high cohesion, single source of truth, DRY principle, YAGNI (you ain't gonna need it). Above all, it's of utmost importance to be pragmatic over being perfect, ensuring there is no over architecting (again, YAGNI).
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}

Step {{ _current_step_index.num }}. **Review for security vulnerabilities:** Analyze the code changes for security concerns including input validation, authentication, authorization, data exposure, injection vulnerabilities, and secure coding practices. Consider both obvious vulnerabilities and subtle security implications.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Review for performance issues:** Evaluate the code changes for performance implications including algorithmic complexity, resource usage, database query efficiency, caching opportunities, unnecessary computations, and scalability concerns.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Review for maintainability:** Assess code maintainability including readability, modularity, naming conventions, code organization, documentation quality, test coverage, technical debt, and adherence to project coding standards.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Review for correctness:** Verify the code logic is correct including edge case handling, error handling, type safety, business logic accuracy, API contract compliance, and proper integration with existing systems.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }} (branch). **Check batch completion:** Perform a branch condition check. Determine if all changed files have been reviewed or if additional batches remain.:
  - Branch {{ _current_step_index.num }}-1 Step 1. **More files to review:** If additional changed files have not yet been reviewed, then return to step {{ _batch_review_step }} for the next batch of files, continuing the systematic pillar-based review process.
  - Branch {{ _current_step_index.num }}-2 Step 1. **Review complete:** If all changed files have been reviewed across all pillars, then proceed to synthesize the complete findings and determine overall review status.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Synthesize findings and determine status:** Consolidate all findings from the pillar-based reviews into a structured array. For each finding, assign severity, specify the pillar, provide detailed description with code context, write actionable recommendations, and include impact analysis for higher-severity items. Write a 2-3 sentence summary of overall code quality. Determine review_status as Approved (no blocking issues), Needs Changes (issues requiring resolution), or Rejected (critical flaws).
{% set _current_step_index.num = _current_step_index.num + 1 %}