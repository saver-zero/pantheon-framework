Step {{ _current_step_index.num }}. **Get the current branch:** Get the current branch. Use `git branch --show-current`
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Get the baseline commit hash:** Get the baseline commit hash. Use `git rev-parse HEAD`
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Get the baseline commit log:** Get the baseline commit log. Use `git log -1 --format=%B HEAD`
{% set _current_step_index.num = _current_step_index.num + 1 %}
