import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MIFOS_API_URL = os.getenv("MIFOS_API_URL", "http://localhost:8080/mifosng/api/v1")
    MIFOS_USERNAME = os.getenv("MIFOS_USERNAME", "mifos")
    MIFOS_PASSWORD = os.getenv("MIFOS_PASSWORD", "password")

    LLM_MODEL = os.getenv("LLM_MODEL", "llama2")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")

    RISK_THRESHOLD_HIGH = float(os.getenv("RISK_THRESHOLD_HIGH", 0.7))
    RISK_THRESHOLD_MEDIUM = float(os.getenv("RISK_THRESHOLD_MEDIUM", 0.4))

    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

config = Config()
