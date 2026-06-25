# Agent Packages

Agents are selected individually, but the first implementation installs them from the shared `lemonade-agents` distribution.

## Available agents

- `supervisor`, `parser`: cashier.
- `onboarder`: inventory.
- `closer`: accounting.
- `drafter`: marketeer.
- `buyer`: supplier.
- `summarizer`: reports.
- `auditor`, `aibom`: security.
- `publisher`: site.

## Dependency rule

Selecting an agent automatically selects its owning department. Selecting a department does not automatically enable every agent; owners/admins choose agents explicitly or select `full-suite-agents`.

## Approval rule

Agents draft and assist. They do not bypass owner approval gates.
