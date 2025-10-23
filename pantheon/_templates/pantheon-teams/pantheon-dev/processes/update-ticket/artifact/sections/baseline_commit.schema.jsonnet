{
  "type": "object",
  "required": [
    "git_branch",
    "baseline_commit_hash",
    "baseline_commit_log"
  ],
  "properties": {
    "git_branch": {
      "description_for_schema": "Current git branch",
      "purpose": "To store the git branch to use for code reviewing with git diff",
      "type": "string"
    },
    "baseline_commit_hash": {
      "description_for_schema": "Git commit hash at the start of ticket work (baseline for code review)",
      "purpose": "The baseline commit to compare against when running 'git diff <hash>...HEAD' for code review",
      "type": "string"
    },
    "baseline_commit_log": {
      "description_for_schema": "Git commit log message for the baseline commit",
      "purpose": "To provide context on what state the codebase was in before ticket work began",
      "type": "string"
    }
  }
}