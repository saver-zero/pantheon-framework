{% set _commit_title = "Phase " + implementation_phase|string + ": " + implementation_phase_name if implementation_phase is defined and implementation_phase_name is defined else commit_description %}
### Commit - {{ _commit_title }}

**Created by:** @{{ pantheon_actor }}  
**Updated:** {{ pantheon_timestamp }}

{{ commit_type }}: [{{ pantheon_artifact_id }}] {{ _commit_title }}

{{ body | wordwrap(88) }}