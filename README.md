# Mifos X Agentic AI Framework

Prototype for the DMP 2026 project: **Agentic AI for Proactive Portfolio Management with Explainable Autonomy**.

The first implementation slice is a deterministic **Portfolio Health Agent** that monitors loan records, scores repayment risk, proposes policy-bound actions, and emits human-readable explanations.

## Why This Shape

The DMP issue asks for agentic autonomy in a regulated financial context. This prototype starts with a transparent, auditable core before adding LLM orchestration. That keeps the safety boundary clear:

- loan risk is explainable
- actions are policy-bound
- high-risk cases are escalated
- autonomy level is explicit
- outputs are suitable for a future officer-review dashboard

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

## Current Scope

Implemented:

- transparent baseline risk scorer
- autonomy policy engine
- portfolio agent orchestration
- JSON input/output CLI
- sample portfolio data
- tests
- architecture notes

Planned:

- Mifos X API adapter
- LangChain/LangGraph orchestration around the deterministic core
- local LLM explanation adapter
- officer-review dashboard integration
- feedback loop and user-study instrumentation
