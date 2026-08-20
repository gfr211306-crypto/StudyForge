# Human feedback log

## Current status

No confirmed human tester records yet.

No `Tester-001` or later ID has been assigned.

## First three ID sequence — not records

The planned assignment order is:

```text
Tester-001 → Tester-002 → Tester-003
```

This line defines the numbering scheme only. It is not three tester records.
Do not create a heading, row, file, or completed entry for any ID until a real
person finishes the Tester Guide and submits feedback.

## Statistics policy

Keep these metrics separate:

- **Human testers:** only people who actually complete the Tester Guide and submit
  feedback.
- **Automated tests:** pytest, CI, E2E matrices, package smoke tests, and health checks.

Automated test runs must never be converted into human tester counts.

## Future anonymized record format

Only add a record after a real person has completed the test and agreed to anonymous
tracking:

```text
Tester-ID:
First feedback date (YYYY-MM):
Environment category:
Workflow completed:
Issues created:
Reproduction status:
Patch release:
```
