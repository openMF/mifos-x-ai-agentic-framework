 Extending the Mifos AI Agent: Developer Guide



Welcome to the core development guide for the Mifos AI Agentic Framework. We are deeply thrilled to have you contribute. This project is built on the profound belief that financial technology should be empathetic, scalable, and community-driven. 



This living document will walk you through the process of extending our AI agent's capabilities, setting up your local environment, and adhering to our strict compliance guardrails.



-------------------



1. Local Development \& Environment Setup

Before extending the agent, you need a safe sandbox to test your ideas without affecting real financial data.



 Prerequisites

 Python 3.10+

 `pipenv` or `conda` for environment management

 Access to a sandbox/test instance of Mifos X (Do NOT use production credentials).



 Setup Steps

1. **Clone your fork:** `git clone https://github.com/<your-username>/mifos-x-ai-agentic-framework.git`

2. **Install dependencies:** `pip install -r requirements.txt`

3. **Environment Variables:** Copy `.env.example` to `.env` and add your test API keys (e.g., OpenAI/Anthropic keys and Mifos Test Tenant URL).

4. **Run the mock server:** Use `python mock_mifos_server.py` to simulate API responses for testing.



--------------------------------------------------



 2. Understanding the Agent's Architecture

Our agent operates on a \*\*Reasoning Engine\*\* (powered by LangChain) and an \*\*Action Executor\*\*. It reads borrower data, reasons through the context using our prompt templates, and suggests actions. 



To extend the agent, you will generally modify one of three areas:

 **Tools:** Giving the agent new abilities (e.g., SMS integration).

 **Prompts:** Changing how the agent "thinks" and formulates empathy.

 **Data Pipelines:** Feeding the agent new types of risk-scoring information.



--------------------------------------------------------------



3. How to Add a New Tool (Action)

Tools are isolated functions the LLM can call. We strictly follow the Single Responsibility Principle.



Navigate to the `agents/tools/` directory and create a new Python script. 



```python

from langchain.tools import tool

import logging



logger = logging.getLogger(\_\_name\_\_)



@tool

def send\_empathetic\_sms(borrower\_phone: str, message: str) -> str:

&#x20;   """

&#x20;   Use this tool to send a restructuring or follow-up SMS to an at-risk borrower.

&#x20;   Requires prior Loan Officer approval in the workflow.

&#x20;   """

&#x20;   try:

&#x20;       # Implementation for external SMS API (e.g., Twilio) goes here

&#x20;       logger.info(f"Compliance Log: SMS drafted for {borrower\_phone}")

&#x20;       return f"SMS successfully queued for {borrower\_phone}"

&#x20;   except Exception as e:

&#x20;       logger.error(f"Failed to send SMS: {str(e)}")

&#x20;       return "Error: Could not execute SMS tool."

