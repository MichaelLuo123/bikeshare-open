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
8. Report the failure, hook behavior, repair steps, and results in docs/SEEDED_FAULTS.md.

Do not evaluate the held-out test set, fabricate evidence, or commit changes automatically.
