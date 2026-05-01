from flask import Flask, jsonify, request
from flask_cors import CORS
from src.config import config
from src.api.mifos_client import MifosClient
from src.agent.portfolio_agent import PortfolioHealthAgent
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize lazily to avoid import errors
_mifos_client = None
_agent = None

def get_agent():
    global _mifos_client, _agent
    if _agent is None:
        _mifos_client = MifosClient(
            config.MIFOS_API_URL,
            config.MIFOS_USERNAME,
            config.MIFOS_PASSWORD
        )
        _agent = PortfolioHealthAgent(_mifos_client)
    return _agent

def get_client():
    global _mifos_client
    if _mifos_client is None:
        _mifos_client = MifosClient(
            config.MIFOS_API_URL,
            config.MIFOS_USERNAME,
            config.MIFOS_PASSWORD
        )
    return _mifos_client

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "portfolio-health-agent"}), 200

@app.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    """Get portfolio overview"""
    try:
        portfolio = get_agent().monitor_portfolio()
        return jsonify(portfolio), 200
    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/portfolio/high-risk", methods=["GET"])
def get_high_risk():
    """Get high-risk accounts only"""
    try:
        portfolio = get_agent().monitor_portfolio()
        return jsonify({
            "count": portfolio["high_risk_count"],
            "accounts": portfolio["high_risk_accounts"]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching high-risk accounts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/account/<int:account_id>/risk", methods=["GET"])
def get_account_risk(account_id):
    """Get risk assessment for specific account"""
    try:
        agent = get_agent()
        account = get_client().get_account_details(account_id)
        score, risk_level, factors = agent.risk_engine.calculate_risk_score(account)
        return jsonify({
            "account_id": account_id,
            "score": score,
            "risk_level": risk_level,
            "factors": factors
        }), 200
    except Exception as e:
        logger.error(f"Error assessing account {account_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/actions", methods=["GET"])
def get_recommended_actions():
    """Get recommended actions for portfolio"""
    try:
        actions = get_agent().process_high_risk_accounts()
        return jsonify({
            "actions": actions,
            "count": len(actions)
        }), 200
    except Exception as e:
        logger.error(f"Error getting actions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/action/<action_id>/approve", methods=["POST"])
def approve_action(action_id):
    """Approve and execute an action"""
    try:
        data = request.json
        action_type = data.get("type")
        client_id = data.get("client_id")
        client = get_client()

        executed = False
        if action_type == "send_reminder":
            executed = client.send_reminder(client_id, data.get("message", ""))
        elif action_type == "schedule_followup":
            executed = client.schedule_followup(client_id, data.get("date"))
        elif action_type == "escalate":
            executed = client.escalate_case(
                client_id,
                data.get("reason"),
                data.get("officer_id", 1)
            )

        return jsonify({
            "action_id": action_id,
            "executed": executed
        }), 200
    except Exception as e:
        logger.error(f"Error executing action: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/action/<action_id>/reject", methods=["POST"])
def reject_action(action_id):
    """Reject an action"""
    data = request.json
    reason = data.get("reason", "No reason provided")
    logger.info(f"Action {action_id} rejected: {reason}")
    return jsonify({
        "action_id": action_id,
        "status": "rejected",
        "reason": reason
    }), 200

@app.route("/api/decisions", methods=["GET"])
def get_decisions_log():
    """Get log of agent decisions"""
    try:
        agent = get_agent()
        return jsonify({
            "decisions": agent.decisions_log,
            "count": len(agent.decisions_log)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching decisions: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=config.DEBUG)
