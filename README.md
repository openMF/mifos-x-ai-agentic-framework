# Mifos X Agentic AI Framework

Implementation branch for the DMP 2026 project: **Agentic AI for Proactive Portfolio Management with Explainable Autonomy**.

The implementation builds a deterministic **Portfolio Health Agent** that monitors loan records, scores repayment risk, proposes policy-bound actions, routes actions through review/execution guards, and emits human-readable explanations.

## Why This Shape

The DMP issue asks for agentic autonomy in a regulated financial context. This prototype starts with a transparent, auditable core before adding LLM orchestration. That keeps the safety boundary clear:

- loan risk is explainable
- actions are policy-bound
- high-risk cases are escalated
- autonomy level is explicit
- review-required actions are queued instead of executed
- outputs are suitable for an officer-review dashboard

## Quickstart

```bash
python -m pip install -e ".[dev]"
mifos-portfolio-agent examples/sample_portfolio.json --out out/portfolio_decisions.json
python -m pytest
```

The CLI writes decisions with:

- loan identifiers
- risk score and band
- feature-level reasons
- proposed action
- human approval flag
- audit metadata
- execution or review-queue status

## Implementation approach

Implemented:

- transparent baseline risk scorer
- autonomy policy engine
- portfolio agent orchestration
- review queue for human approval workflows
- safe action executor that refuses to bypass approval
- Mifos X API adapter boundary for live loan payloads
- JSON input/output CLI
- sample portfolio data
- tests

Planned:

- LangChain/LangGraph orchestration around the deterministic core
- local LLM explanation adapter
- officer-review dashboard integration
- feedback loop and user-study instrumentation

## Repository structure

```text
src/mifos_agentic/
  actions.py    review queue and guarded action execution
  agent.py      PortfolioHealthAgent orchestration
  cli.py        command line interface
  io.py         JSON portfolio loading and writing
  mifos_api.py  Mifos X API adapter boundary
  models.py     loan, risk, and action dataclasses
  policy.py     autonomy policy rules
  risk.py       explainable baseline risk scorer
examples/
  sample_portfolio.json
tests/
  test_agent.py
```

## Safety boundary

The default mode is `recommend_only`. In this mode the agent can score accounts and propose actions, but approval-gated actions are queued for review. `bounded_execute` only auto-executes low-risk actions that fall under configured thresholds. Critical and high-risk loans are escalated to officers.
