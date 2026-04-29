# Portfolio Health Agent - API Reference

Base URL: `http://localhost:5000/api`

## Health Check

### GET /health

Check if the service is running.

**Response:**
```json
{
  "status": "ok",
  "service": "portfolio-health-agent"
}
```

---

## Portfolio Endpoints

### GET /portfolio

Get complete portfolio overview with all risk categories.

**Response:**
```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00",
  "high_risk_count": 5,
  "medium_risk_count": 12,
  "high_risk_accounts": [
    {
      "account_id": 101,
      "client_id": 1,
      "client_name": "John Doe",
      "risk_score": 0.85,
      "risk_level": "HIGH",
      "factors": {
        "arrears_days": 120,
        "repayment_rate": 0.3,
        "account_age": 8,
        "loan_ratio": 0.75,
        "missed_payments": 3
      }
    }
  ],
  "medium_risk_accounts": [...]
}
```

### GET /portfolio/high-risk

Get only high-risk accounts (score ≥ 0.7).

**Response:**
```json
{
  "count": 5,
  "accounts": [...]
}
```

---

## Account Endpoints

### GET /account/{account_id}/risk

Get risk assessment for a specific account.

**Parameters:**
- `account_id` (path, required): Loan account ID

**Response:**
```json
{
  "account_id": 101,
  "score": 0.75,
  "risk_level": "HIGH",
  "factors": {
    "arrears_days": 90,
    "repayment_rate": 0.4,
    "account_age": 6,
    "loan_ratio": 0.65,
    "missed_payments": 2
  }
}
```

---

## Action Endpoints

### GET /actions

Get all recommended actions for high-risk accounts.

**Response:**
```json
{
  "actions": [
    {
      "account_id": 101,
      "action": "send_reminder",
      "reason": "Account 60 days in arrears",
      "executed": false
    },
    {
      "account_id": 102,
      "action": "escalate",
      "reason": "Account 120 days in arrears with risk score 0.85",
      "executed": false
    }
  ],
  "count": 2
}
```

**Action Types:**
- `send_reminder`: Send payment reminder to client
- `schedule_followup`: Schedule check-in with client
- `escalate`: Escalate to loan officer for manual intervention

### POST /action/{action_id}/approve

Approve and execute a recommended action.

**Parameters:**
- `action_id` (path, required): Action identifier

**Request Body:**
```json
{
  "type": "send_reminder",
  "client_id": 1,
  "message": "Please make your loan payment",
  "date": "2024-01-20",
  "officer_id": 1
}
```

**Response:**
```json
{
  "action_id": "action_101",
  "executed": true
}
```

**Status Codes:**
- `200`: Action executed successfully
- `400`: Invalid action data
- `500`: Execution failed

### POST /action/{action_id}/reject

Reject a recommended action with optional feedback.

**Request Body:**
```json
{
  "reason": "Client already contacted yesterday"
}
```

**Response:**
```json
{
  "action_id": "action_101",
  "status": "rejected",
  "reason": "Client already contacted yesterday"
}
```

---

## Decision History

### GET /decisions

Get log of all agent decisions and actions.

**Response:**
```json
{
  "decisions": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "account": {
        "account_id": 101,
        "client_id": 1,
        "client_name": "John Doe",
        "risk_score": 0.85,
        "risk_level": "HIGH",
        "factors": {...}
      },
      "action": {
        "account_id": 101,
        "action": "escalate",
        "reason": "Account 120 days in arrears",
        "executed": false
      }
    }
  ],
  "count": 42
}
```

---

## Error Handling

All errors return JSON with error message:

```json
{
  "error": "Description of what went wrong"
}
```

**Common Error Cases:**

| Status | Error | Cause |
|--------|-------|-------|
| 400 | Invalid account ID | Account doesn't exist in Mifos X |
| 404 | Endpoint not found | URL path is incorrect |
| 500 | Mifos X connection failed | API unreachable or auth failed |
| 500 | LLM service unavailable | Local model not running |

---

## Rate Limiting

No explicit rate limiting currently. For production:
- Implement rate limiting (e.g., 100 req/min per IP)
- Add request queuing for monitoring tasks
- Cache portfolio snapshots (5-10 min TTL)

---

## Authentication

Current version uses basic HTTP. For production, implement:

```
Authorization: Bearer <token>
```

Or use API keys:

```
X-API-Key: <key>
```

---

## Example Workflows

### Monitor Portfolio
```bash
curl http://localhost:5000/api/portfolio
```

### Check Specific Account
```bash
curl http://localhost:5000/api/account/101/risk
```

### Get Actions and Approve
```bash
# Get recommended actions
curl http://localhost:5000/api/actions

# Approve an action
curl -X POST http://localhost:5000/api/action/action_101/approve \
  -H "Content-Type: application/json" \
  -d '{
    "type": "send_reminder",
    "client_id": 1,
    "message": "Please make payment"
  }'
```

### View Decision History
```bash
curl http://localhost:5000/api/decisions | jq '.decisions[0]'
```

---

## Integration Examples

### Python
```python
import requests

api_url = "http://localhost:5000/api"

# Get portfolio
portfolio = requests.get(f"{api_url}/portfolio").json()
print(f"High-risk accounts: {portfolio['high_risk_count']}")

# Approve action
requests.post(f"{api_url}/action/action_101/approve", json={
    "type": "send_reminder",
    "client_id": 1
})
```

### JavaScript/Node.js
```javascript
const api = 'http://localhost:5000/api';

// Get portfolio
const portfolio = await fetch(`${api}/portfolio`).then(r => r.json());
console.log(`High-risk: ${portfolio.high_risk_count}`);

// Approve action
await fetch(`${api}/action/action_101/approve`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    type: 'send_reminder',
    client_id: 1
  })
});
```

### cURL
```bash
# Check health
curl http://localhost:5000/api/health

# Get portfolio
curl http://localhost:5000/api/portfolio

# Get high-risk accounts
curl http://localhost:5000/api/portfolio/high-risk
```
