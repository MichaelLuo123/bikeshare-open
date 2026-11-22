---
name: seed-fault
description: Safely seed, test, document, and restore a deliberate fault in the bikeshare pipeline.
allowed-tools: Read, Edit, Bash
---

# Seed and verify a fault: $ARGUMENTS

1. Identify the exact file, function, and expected failure described by $ARGUMENTS.
2. Check git status and do not overwrite unrelated changes.
3. Run relevant tests and verify they pass before making changes.
4. Introduce only the specified fault. Never modify data/raw/.
5. Run tests and capture the actual failing output.
6. Record whether the PostToolUse hook detected the fault. Do not invent hook output.
7. Restore the original implementation and rerun tests.
8. Append a new dated section to docs/SEEDED_FAULTS.md containing the actual failure, hook behavior, repair steps, and test results.
9. Preserve all existing documentation exactly. Never overwrite, replace, or rewrite docs/SEEDED_FAULTS.md.
10. Append the new section ONLY at the absolute end of the file, after all existing sections. Never insert it beneath an existing heading or inside another fault's documentation.
11. Before applying the edit, verify that the entire existing file remains an unchanged prefix of the proposed file. If this cannot be guaranteed, provide the new entry in your response instead of editing the file.

Do not evaluate the held-out test set, fabricate evidence, or commit changes automatically.
