from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM Provider
    llm_provider: str = "default"
    llm_api_key: str = "default"
    llm_model_name: str = "default"

    # SAP S4HANA
    sap_api_url: str = "default"
    sap_api_key: str = "default"

    # ServiceNow
    servicenow_instance_url: str = "default"
    servicenow_username: str = "default"
    servicenow_password: str = "default"

    # Redis (for short-term memory)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None

    # SAP HANA Cloud DB (for long-term memory)
    hana_db_address: str = "default"
    hana_db_port: int = 5432
    hana_db_user: str = "default"
    hana_db_password: str = "default"
    hana_db_database: str = "default"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
