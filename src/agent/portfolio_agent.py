from typing import List, Dict, Any
from datetime import datetime, timedelta
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.api.mifos_client import MifosClient
from src.risk_scorer.risk_assessment import RiskAssessmentEngine
from src.config import config

class PortfolioHealthAgent:
    def __init__(self, mifos_client: MifosClient):
        self.mifos_client = mifos_client
        self.risk_engine = RiskAssessmentEngine()
        self.llm = self._init_llm()
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.decisions_log = []

    def _init_llm(self):
        """Initialize LLM (using local Ollama or OpenAI)"""
        return ChatOpenAI(
            model=config.LLM_MODEL,
            temperature=0.3,
            api_key="dummy"
        )

    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        tools = [
            Tool(
                name="get_portfolio_snapshot",
                func=self._get_portfolio_snapshot,
                description="Get current portfolio overview with risk summary"
            ),
            Tool(
                name="assess_account_risk",
                func=self._assess_single_account,
                description="Assess risk for a specific loan account"
            ),
            Tool(
                name="send_client_reminder",
                func=self._send_reminder,
                description="Send reminder to client about upcoming payment"
            ),
            Tool(
                name="schedule_followup",
                func=self._schedule_followup,
                description="Schedule follow-up with a client"
            ),
            Tool(
                name="escalate_to_officer",
                func=self._escalate_case,
                description="Escalate complex case to loan officer for review"
            )
        ]
        return tools

    def _create_agent(self):
        """Create the React agent"""
        from langchain.prompts import PromptTemplate

        prompt = PromptTemplate.from_template("""You are a Portfolio Health Agent for a microfinance institution. Your role is to:
1. Monitor loan portfolios for accounts at risk
2. Identify patterns and trends
3. Execute pre-approved actions like sending reminders or scheduling follow-ups
4. Escalate complex cases requiring human judgment

You have access to the following tools:
{tools}

Tool names: {tool_names}

Always provide clear reasoning for your decisions.

Current date: {current_date}

{agent_scratchpad}

Question: {input}
""")

        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True
        )

    def monitor_portfolio(self) -> Dict[str, Any]:
        """Main monitoring function"""
        clients = self.mifos_client.get_clients()
        if not clients:
            return {"status": "error", "message": "Could not fetch clients"}

        high_risk_accounts = []
        medium_risk_accounts = []

        for client in clients:
            accounts = self.mifos_client.get_client_accounts(client["id"])
            for account in accounts:
                score, risk_level, factors = self.risk_engine.calculate_risk_score(account)

                account_info = {
                    "account_id": account.get("id"),
                    "client_id": client.get("id"),
                    "client_name": client.get("displayName"),
                    "risk_score": score,
                    "risk_level": risk_level,
                    "factors": factors
                }

                if risk_level == "HIGH":
                    high_risk_accounts.append(account_info)
                elif risk_level == "MEDIUM":
                    medium_risk_accounts.append(account_info)

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "high_risk_count": len(high_risk_accounts),
            "medium_risk_count": len(medium_risk_accounts),
            "high_risk_accounts": high_risk_accounts,
            "medium_risk_accounts": medium_risk_accounts
        }

    def process_high_risk_accounts(self) -> List[Dict[str, Any]]:
        """Process high-risk accounts and execute actions"""
        portfolio = self.monitor_portfolio()
        actions = []

        for account in portfolio.get("high_risk_accounts", []):
            action = self._decide_action(account)
            actions.append(action)
            self.decisions_log.append({
                "timestamp": datetime.now().isoformat(),
                "account": account,
                "action": action
            })

        return actions

    def _decide_action(self, account: Dict[str, Any]) -> Dict[str, Any]:
        """Decide what action to take for an account"""
        arrears = account["factors"].get("arrears_days", 0)
        score = account["risk_score"]

        if arrears > 90:
            return {
                "account_id": account["account_id"],
                "action": "escalate",
                "reason": f"Account {arrears} days in arrears with risk score {score:.2f}",
                "executed": False
            }
        elif arrears > 30:
            return {
                "account_id": account["account_id"],
                "action": "send_reminder",
                "reason": f"Account {arrears} days in arrears",
                "executed": False
            }
        else:
            return {
                "account_id": account["account_id"],
                "action": "schedule_followup",
                "reason": f"High risk score {score:.2f}, schedule check-in",
                "executed": False
            }

    def _get_portfolio_snapshot(self, _: str = "") -> str:
        """Get portfolio overview"""
        portfolio = self.monitor_portfolio()
        return f"High Risk: {portfolio['high_risk_count']}, Medium Risk: {portfolio['medium_risk_count']}"

    def _assess_single_account(self, account_id: str) -> str:
        """Assess a single account"""
        account = self.mifos_client.get_account_details(int(account_id))
        score, risk_level, factors = self.risk_engine.calculate_risk_score(account)
        return f"Risk Score: {score:.2f}, Level: {risk_level}, Factors: {factors}"

    def _send_reminder(self, client_id: str) -> str:
        """Send reminder"""
        success = self.mifos_client.send_reminder(
            int(client_id),
            "You have an upcoming loan payment due. Please arrange payment."
        )
        return "Reminder sent" if success else "Failed to send reminder"

    def _schedule_followup(self, client_id: str) -> str:
        """Schedule follow-up"""
        followup_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        success = self.mifos_client.schedule_followup(int(client_id), followup_date)
        return f"Follow-up scheduled for {followup_date}" if success else "Failed to schedule"

    def _escalate_case(self, client_id: str) -> str:
        """Escalate case"""
        success = self.mifos_client.escalate_case(
            int(client_id),
            "High risk account requiring officer attention",
            1
        )
        return "Case escalated" if success else "Failed to escalate"
