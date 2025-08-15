import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class Config:
    """
    Handles loading and validation of configuration from environment variables.
    
    This approach avoids hardcoding sensitive information like API keys in the source code,
    which is a critical security best practice.
    """
    tecton_url: str
    api_key: str
    workspace_name: str
    api_service: str

    def __init__(self) -> None:
        """
        Initializes the Config object by reading from the environment.
        
        Raises:
            ConfigError: If any of the required environment variables are not set.
        """
        self.tecton_url = os.environ.get("TECTON_URL", "")
        self.api_key = os.environ.get("TECTON_API_KEY", "")
        self.workspace_name = os.environ.get("TECTON_WORKSPACE", "")
        self.api_service = os.environ.get("API_SERVICE", "")

        if not all([self.tecton_url, self.api_key, self.workspace_name, self.api_service]):
            raise ConfigError(
                "Missing required environment variables. "
                "Please set TECTON_URL, TECTON_API_KEY, TECTON_WORKSPACE, and API_SERVICE."
            )

# --- Global Config Instance ---
# A single, globally accessible config object is instantiated.
# A try-except block handles the case where the script is imported in an
# environment without the variables set (e.g., during linting or docs generation),
# preventing a crash on import. The error will be caught at runtime instead.
config: Optional[Config]
try:
    config = Config()
except ConfigError:
    config = None