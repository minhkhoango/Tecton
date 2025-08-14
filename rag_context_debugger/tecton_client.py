from typing import Dict, Any, Optional

# Library imports
from tecton.framework.workspace import Workspace, get_workspace
from tecton.framework.data_frame import FeatureVector
from tecton.identities.credentials import login

# Local application imports
from .config import config, ConfigError

class TectonDebuggerClient:
    """
    A wrapper for the Tecton SDK to simplify fetching context vectors.

    This class abstracts away the details of initialization, request formation,
    and error handling, providing a clean interface for the rest of the application.
    """
    workspace: Workspace

    def __init__(self) -> None:
        """
        Initializes the Tecton client and logs into the specified workspace.

        Raises:
            ConfigError: If configuration is not loaded.
            ConnectionError: If connection or authentication with Tecton fails.
        """
        if config is None:
            raise ConfigError("Configuration not loaded. Check environment variables.")
        
        try:
            # tecton.login authenticates the session
            login(config.tecton_url, interactive=False, tecton_api_key=config.api_key)
            # tecton.get_workspace returns the workspace instance
            self.workspace = get_workspace(config.workspace_name)
        except Exception as e:
            # Provide a more user-friendly error message for common connection issues.
            raise ConnectionError(f"Failed to connect or authenticate with Tecton. Check URL and API Key. Details: {e}")

    def fetch_context_vector(
        self,
        service_name: str,
        join_keys: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None
    ) -> FeatureVector:
        """
        Fetches the online feature vector for a given service and join keys.

        Args:
            service_name: The name of the Tecton Feature Service.
            join_keys: A dictionary of the primary keys for the feature lookup.
            request_data: An optional dictionary for on-demand feature context.

        Returns:
            A Tecton FeatureVector object.

        Raises:
            ValueError: If the FeatureService is not found.
            RuntimeError: For other Tecton server errors or unexpected issues.
        """
        try:
            feature_service = self.workspace.get_feature_service(service_name)
            
            # This is the core SDK call to retrieve online features.
            # .get_online_features() returns a FeatureVector directly.
            feature_vector = feature_service.get_online_features(
                join_keys=join_keys,
                request_data=request_data or {}
            )
            return feature_vector
            
        except Exception as e:
            # Intercept common errors to provide clearer feedback to the user.
            if "not found" in str(e).lower():
                if config is not None:
                    raise ValueError(f"FeatureService '{service_name}' not found in workspace '{config.workspace_name}'.")
                else:
                    raise ValueError(f"FeatureService '{service_name}' not found.")
            else:
                raise RuntimeError(f"Tecton server error: {e}")