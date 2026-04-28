# Portfolio Health Agent Architecture

## First Prototype

The prototype is deliberately deterministic and auditable:

1. Load loan portfolio records from JSON.
2. Score each loan with transparent feature contributions.
3. Select a policy-bound action:
   - `send_reminder`
   - `schedule_follow_up`
   - `escalate_to_officer`
   - `none`
4. Attach a human-readable explanation and review flag.
5. Write JSON decisions for dashboard or API integration.

This gives loan officers and mentors a reviewable baseline before introducing LangChain/LangGraph, local LLMs, or live Mifos X API calls.

## Agent Safety Principles

- High-risk accounts are escalated to humans, not auto-executed.
- Every decision includes a score, band, reasons, and feature contributions.
- `recommend_only` is the default autonomy level.
- `bounded_execute` can only auto-execute low/medium bounded actions below configured thresholds.
- The output is audit-friendly JSON that can be stored, reviewed, and replayed.

## Next Integration Steps

- Add a Mifos X API adapter for `/loans` and repayment schedule endpoints.
- Replace local JSON input with authenticated API fetches.
- Add LangGraph/LangChain nodes around the deterministic core:
  - fetch portfolio
  - assess risk
  - policy check
  - propose action
  - human review
  - execute approved action
- Build a simple dashboard panel for officer review and feedback.
- Add user-study instrumentation for trust/usability evaluation.
