# Portfolio Health Agent Documentation

## Overview

The Portfolio Health Agent is an autonomous AI system built with LangChain that monitors loan portfolios and makes intelligent decisions about which accounts need intervention.

## Agent Architecture

### Components

1. **Risk Assessment Engine**: Calculates risk scores for accounts
2. **Mifos X API Client**: Integrates with Mifos X to fetch account data
3. **LangChain Agent**: Uses React pattern to reason and take actions
4. **Action Executor**: Executes approved actions (reminders, follow-ups, escalations)

### Decision Flow

```
Monitor Portfolio
    ↓
Calculate Risk Scores
    ↓
Identify High-Risk Accounts
    ↓
Recommend Actions
    ↓
Loan Officer Review (Human-in-the-Loop)
    ↓
Execute Approved Actions
    ↓
Log Decisions
```

## Agent Tools

The agent has access to the following tools:

### get_portfolio_snapshot
- **Purpose**: Get overview of portfolio risk distribution
- **Returns**: Count of high-risk and medium-risk accounts
- **Triggered by**: Portfolio monitoring queries

### assess_account_risk
- **Purpose**: Detailed risk assessment for a specific account
- **Input**: Account ID
- **Returns**: Risk score, level, and detailed factors
- **Triggered by**: When examining specific problem accounts

### send_client_reminder
- **Purpose**: Send payment reminder to client
- **Input**: Client ID
- **Returns**: Success/failure status
- **Triggered by**: Accounts 30-90 days in arrears

### schedule_followup
- **Purpose**: Schedule follow-up interaction with client
- **Input**: Client ID
- **Returns**: Follow-up date and status
- **Triggered by**: Medium-risk accounts
- **Default Schedule**: 7 days from current date

### escalate_to_officer
- **Purpose**: Escalate complex case to loan officer
- **Input**: Client ID, reason for escalation
- **Returns**: Escalation status and officer assignment
- **Triggered by**: Accounts >90 days in arrears or complex situations

## Action Selection Logic

The agent follows this decision tree:

```
Account Risk Assessment
    ├─ HIGH RISK (score ≥ 0.7)
    │  ├─ Arrears > 90 days → Escalate to Officer
    │  ├─ Arrears 30-90 days → Send Reminder
    │  └─ Arrears < 30 days → Schedule Follow-up
    │
    ├─ MEDIUM RISK (0.4 ≤ score < 0.7)
    │  └─ Schedule Follow-up
    │
    └─ LOW RISK (score < 0.4)
       └─ No action needed
```

## Agent Configuration

The agent can be customized through environment variables:

- **LLM_MODEL**: Which language model to use (default: llama2)
- **LLM_BASE_URL**: Where to find the LLM service
- **RISK_THRESHOLD_HIGH**: Score threshold for HIGH risk (default: 0.7)
- **RISK_THRESHOLD_MEDIUM**: Score threshold for MEDIUM risk (default: 0.4)

## Decision Logging

All agent decisions are logged with:
- Timestamp
- Account details
- Risk assessment
- Action recommended
- Reasoning (from agent)
- Approval status

This enables:
- Audit trails for regulatory compliance
- Performance analysis of recommendations
- Feedback loops for model improvement
- Transparency to loan officers

## Extending the Agent

### Adding New Tools

1. Create a method in `PortfolioHealthAgent`
2. Wrap it as a LangChain Tool
3. Add to `_create_tools()` list
4. Update agent prompt if needed

Example:
```python
Tool(
    name="send_email",
    func=self._send_email,
    description="Send email to client"
)
```

### Adding New Reasoning

Modify the agent prompt in `_create_agent()` to guide decision-making:
- Add constraints (e.g., "prioritize newer accounts")
- Add decision criteria
- Provide examples of good decisions

### Adding New Data Sources

1. Extend `MifosClient` with new API methods
2. Add calculations to `RiskAssessmentEngine`
3. Update agent tools to use new data

## Performance Monitoring

Key metrics to track:

- **Action Accuracy**: % of recommended actions approved by officers
- **Risk Assessment Accuracy**: How well predictions match actual outcomes
- **Processing Time**: Latency for portfolio monitoring
- **Coverage**: % of portfolio assessed each monitoring cycle

## Best Practices

1. **Start Conservative**: Set high thresholds initially, lower over time
2. **Monitor Manually**: Review agent recommendations before full autonomy
3. **Gather Feedback**: Collect loan officer feedback on decisions
4. **Iterate**: Adjust weights and thresholds based on results
5. **Audit**: Regularly review decision logs
6. **Document**: Keep clear records of changes and their rationale

## Troubleshooting

### Agent Not Making Decisions

1. Check Mifos X connection (verify MIFOS_API_URL)
2. Verify LLM service is running
3. Check logs for API errors

### Poor Risk Predictions

1. Analyze decision logs
2. Compare agent scores to actual outcomes
3. Adjust risk weights in `calculate_risk_score()`
4. Retrain on historical data (future enhancement)

### Actions Not Executing

1. Verify officer is approving actions
2. Check Mifos X API permissions
3. Review escalation flow
4. Check action logs for errors
