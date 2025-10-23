## Team Profile Configuration
updated_at: {{ pantheon_timestamp }}

### Configuration Overview

{{ profile_overview }}

{% if property_definitions %}
### Configuration Properties

{% for prop_name, prop_def in property_definitions.items() %}
#### {{ prop_name }}

**Type**: {{ prop_def.property_type }}

**Description**: {{ prop_def.property_description }}

**Options**:
{% for option in prop_def.options %}
- **{{ option.value | lower }}**: {{ option.description }}
{% endfor %}

{% endfor %}
{% endif %}

{% if profiles %}
### Available Profiles

{% if default_profile %}
**Default Profile**: {{ default_profile }}

{% endif %}
{% for profile_name, profile_values in profiles.items() %}
#### {{ profile_name }}
{% for prop_name, prop_value in profile_values.items() %}
- **{{ prop_name }}**: {{ prop_value | lower }}
{% endfor %}

{% endfor %}
{% else %}
### Profile Configuration

No configuration profiles required for this team. The team operates with a single, consistent configuration.
{% endif %}