local rules = {
  // Rule factory for creating a standard transformation object
  makeRule(comment, pattern, replacement): {
    _comment: comment,
    pattern: pattern,
    replacement: replacement,
  },

  // Strip leading/trailing whitespace
  stripWhitespace: self.makeRule(
    'Strip leading/trailing whitespace',
    '^\\s+|\\s+$',
    ''
  ),

  // Extract basename from a path
  extractBasename: self.makeRule(
    'Extract basename from a path',
    '.*[\\\\\/]',
    ''
  ),

  // Remove .md extension if present
  removeExtension: self.makeRule(
    'Remove .md extension',
    '\\.md$',
    ''
  ),

  // Extract ticket ID (T12 from T12-something)
  extractTicketId: self.makeRule(
    'Extract ticket ID before first hyphen',
    '^(T\\d+)-.*$',
    '$1'
  ),
};

// Apply rules in order to extract ticket ID
[
  rules.stripWhitespace,
  rules.extractBasename,
  rules.removeExtension,
  rules.extractTicketId,
]