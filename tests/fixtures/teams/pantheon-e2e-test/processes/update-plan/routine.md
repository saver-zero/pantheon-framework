# Create Ticket Routine

## Process Overview
This routine creates a new ticket artifact with structured description and plan sections.

## Steps

### Step 1: Get Process Schema
Retrieve the JSON schema for this process to understand required data structure.

```bash
pantheon get schema update-plan --actor ticket-handler
```

### Step 2: Get Temporary File
Get a temporary file path for atomic operation processing.

```bash
pantheon project get tempfile --process create-ticket --actor ticket-handler
```

### Step 3: Validate Input Data
Ensure the input JSON contains all required fields (ticket_id, description, plan) and matches the schema retrieved in Step 1.

### Step 4: Execute Process (Terminating)
Execute the create-ticket process using the validated JSON data from the temporary file.

```bash
pantheon execute update-plan --from-file [TEMP_FILE_PATH] --actor ticket-handler
```

**Result**: The specified ticket's plan will be updated.