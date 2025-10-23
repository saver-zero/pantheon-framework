# Get Ticket Routine

## Process Overview
This routine retrieves an existing ticket artifact and returns its content as structured JSON.

## Steps

### Step 1. Execute Get Ticket (Terminating)
Use the pantheon CLI to retrieve the ticket with the specified ticket_id.

```bash
pantheon execute get-ticket --actor ticket-handler --id <ticket_id>
```

**Result**: The command will return the ticket content.