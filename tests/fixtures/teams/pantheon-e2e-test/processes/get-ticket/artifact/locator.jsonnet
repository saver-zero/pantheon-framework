{
  // Directory to search for ticket files
  directory: "tickets",
  
  // Get the artifact ID from external variable
  local id = std.extVar("pantheon_artifact_id"),
  
  // Regex pattern to find ticket files by specific ID
  pattern: "^" + id + "-.*[.]md$"
}