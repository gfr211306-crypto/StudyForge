# Human feedback log

## Current status

No confirmed human tester records yet.

No `Tester-001` or later ID has been assigned.

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
