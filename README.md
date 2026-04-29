# Mifos X Portfolio Health Agent

An agentic AI framework for autonomous loan portfolio monitoring and management in Mifos X (a financial inclusion platform). The system uses LangChain and local language models to intelligently assess portfolio risk and execute pre-approved actions.

## Features

- **Portfolio Monitoring**: Continuously monitor loan accounts for risk indicators
- **Risk Assessment**: Algorithmic scoring based on arrears, repayment rate, account age, and loan ratios
- **Autonomous Actions**: Send reminders, schedule follow-ups, and escalate cases automatically
- **Explainable AI**: Transparent decision-making with detailed reasoning
- **Human-in-the-Loop**: Loan officers review and approve/reject actions before execution
- **Dashboard**: Web interface for portfolio oversight and decision management

## Architecture

```
src/
├── agent/              # LangChain-based portfolio health agent
├── api/                # Mifos X API client for data integration
├── risk_scorer/        # Risk assessment engine
├── dashboard/          # Flask web dashboard
└── config.py           # Configuration management
```

## Prerequisites

- Python 3.8+
- Mifos X instance with API access
- Local LLM (Ollama, LM Studio) or OpenAI API key
- pip (Python package manager)

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd mifos-x-portfolio-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Mifos X and LLM credentials
```

## Configuration

Edit `.env` file with your settings:

- **MIFOS_API_URL**: URL of your Mifos X instance
- **MIFOS_USERNAME/PASSWORD**: Mifos X API credentials
- **LLM_MODEL**: Name of local model (e.g., "llama2")
- **LLM_BASE_URL**: URL of local LLM service (e.g., Ollama)
- **RISK_THRESHOLD_HIGH**: Score threshold for high-risk accounts (0-1)
- **RISK_THRESHOLD_MEDIUM**: Score threshold for medium-risk accounts (0-1)

## Running the System

### Start the Dashboard
```bash
python -m src.dashboard.app
```

The dashboard will be available at `http://localhost:5000`

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/portfolio` - Get portfolio overview
- `GET /api/portfolio/high-risk` - Get high-risk accounts
- `GET /api/account/<id>/risk` - Get risk assessment for specific account
- `GET /api/actions` - Get recommended actions
- `POST /api/action/<id>/approve` - Approve and execute action
- `POST /api/action/<id>/reject` - Reject action
- `GET /api/decisions` - Get log of agent decisions

## Risk Scoring

The risk assessment engine evaluates accounts based on:

1. **Arrears Days** (35%): Number of days overdue
2. **Repayment Rate** (25%): On-time payment history
3. **Account Age** (15%): Newer accounts weighted higher
4. **Loan Amount Ratio** (15%): Outstanding vs. original principal
5. **Missed Payments** (10%): Count of payment defaults

Risk levels:
- **HIGH**: Score ≥ 0.7 (immediate action needed)
- **MEDIUM**: Score 0.4-0.7 (monitoring and follow-up)
- **LOW**: Score < 0.4 (normal operations)

## Agent Decision Making

The Portfolio Health Agent uses LangChain to reason about portfolio state:

- **Assess**: Evaluate account risk using algorithmic scoring
- **Decide**: Determine appropriate action based on risk factors
- **Act**: Execute pre-approved actions (reminders, follow-ups, escalations)
- **Learn**: Log decisions for audit and continuous improvement

Actions taken:
- **Send Reminder**: For accounts 30-90 days in arrears
- **Schedule Follow-up**: For high-risk accounts requiring check-in
- **Escalate**: For accounts >90 days in arrears, requiring officer intervention

## Testing

Run tests:
```bash
pytest tests/
```

## Development

To add new risk factors:
1. Modify `src/risk_scorer/risk_assessment.py`
2. Add new calculation method
3. Adjust weights in `calculate_risk_score()`
4. Update documentation

To add agent tools:
1. Create method in `PortfolioHealthAgent`
2. Add to `_create_tools()` list
3. Update dashboard endpoints if needed

## Feedback & Adjustments

Loan officers can:
- Review recommended actions before execution
- Provide feedback on accuracy
- Adjust autonomy settings for future decisions
- View decision reasoning and factors

## Documentation

- `docs/` - Architecture and design documents
- `docs/API.md` - API reference
- `docs/AGENT.md` - Agent behavior and decision logic
- `docs/RISK_SCORING.md` - Risk assessment details

## Contributing

1. Create a feature branch
2. Make changes and test thoroughly
3. Submit pull request with clear description
4. Include any updated documentation

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check existing GitHub issues
2. Create new issue with detailed description
3. Contact Mifos X community

## Acknowledgments

Built with:
- [LangChain](https://python.langchain.com/) - Agent framework
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Mifos X](https://mifos.org/) - Financial inclusion platform
