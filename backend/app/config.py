import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "RevenueSystem - AI Revenue Growth Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./revenue_system.db")

    # Razorpay Test Mode
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "placeholder_secret")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "test_webhook_secret_123")

    # Claude AI
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Merchant Policy Guardrail Defaults
    DEFAULT_MAX_AUTONOMOUS_DISCOUNT: float = float(os.getenv("DEFAULT_MAX_AUTONOMOUS_DISCOUNT", "10.0"))
    DEFAULT_MAX_CAMPAIGN_BUDGET: float = float(os.getenv("DEFAULT_MAX_CAMPAIGN_BUDGET", "20000.0"))
    MAX_AUTONOMOUS_TRANSACTION: float = 5000.0
    AUTONOMOUS_REFUNDS_ENABLED: bool = False

settings = Settings()
