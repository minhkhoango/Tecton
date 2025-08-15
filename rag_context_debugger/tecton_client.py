from typing import Dict, Any, Optional
import logging

# Library imports
from tecton.framework.workspace import Workspace, get_workspace
from tecton.framework.data_frame import FeatureVector
from tecton.framework.feature_service import FeatureService
from tecton.identities.credentials import login

# Local application imports
from .config import config, ConfigError

# Configure logging for debugging and monitoring
logger = logging.getLogger(__name__)

class TectonDebuggerClient:
    """
    A production-ready wrapper for the Tecton SDK to simplify fetching context vectors.

    This class implements comprehensive error handling and provides clear, actionable
    feedback for all failure scenarios. It's designed to be robust even when the
    Tecton environment is unstable or misconfigured.
    """
    
    def __init__(self) -> None:
        """
        Initializes the Tecton client and logs into the specified workspace.

        This method implements isolated error handling for connection and authentication
        failures, providing specific guidance for each failure mode.

        Raises:
            ConfigError: If configuration is not loaded.
            ConnectionError: If connection or authentication with Tecton fails.
        """
        if config is None:
            raise ConfigError("Configuration not loaded. Check environment variables.")
        
        # Step 1: Attempt to authenticate with Tecton
        try:
            logger.debug(f"Attempting to authenticate with Tecton at {config.tecton_url}")
            login(
                config.tecton_url, 
                interactive=False, 
                tecton_api_key=config.api_key
            )
            logger.debug("Tecton authentication successful")
        except Exception as auth_error:
            logger.error(f"Tecton authentication failed: {auth_error}")
            raise ConnectionError(
                f"Failed to authenticate with Tecton. Please verify your TECTON_URL and "
                f"TECTON_API_KEY are correct and that your API key has not expired. "
                f"Downstream error: {auth_error}"
            )
        
        # Step 2: Attempt to connect to the specified workspace
        try:
            logger.debug(f"Attempting to connect to workspace: {config.workspace_name}")
            self.workspace: Workspace = get_workspace(config.workspace_name)
            logger.debug(f"Successfully connected to workspace: {config.workspace_name}")
        except Exception as workspace_error:
            logger.error(f"Workspace connection failed: {workspace_error}")
            raise ConnectionError(
                f"Failed to connect to Tecton workspace '{config.workspace_name}'. "
                f"Please verify the TECTON_WORKSPACE name is correct and that your "
                f"API key has access to this workspace. Downstream error: {workspace_error}"
            )

    def fetch_context_vector(
        self,
        service_name: str,
        join_keys: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None
    ) -> FeatureVector:
        """
        Fetches the online feature vector for a given service and join keys.

        This method implements granular error handling for each step of the feature
        retrieval process, providing specific guidance for different failure modes.

        Args:
            service_name: The name of the Tecton Feature Service.
            join_keys: A dictionary of the primary keys for the feature lookup.
            request_data: An optional dictionary for on-demand feature context.

        Returns:
            A Tecton FeatureVector object compatible with FeatureVectorProtocol.

        Raises:
            ValueError: If the FeatureService is not found or inputs are invalid.
            ConnectionError: If authentication/permission issues occur.
            RuntimeError: For Tecton server errors or unexpected issues.
        """
        if not service_name or not service_name.strip():
            raise ValueError("Service name cannot be empty or whitespace.")
        
        if not join_keys:
            raise ValueError("Join keys cannot be empty. Please provide valid join keys.")
        
        # Step 4.1: Retrieve the Feature Service
        try:
            logger.debug(f"Attempting to retrieve Feature Service: {service_name}")
            feature_service: FeatureService = self.workspace.get_feature_service(service_name)
            logger.debug(f"Successfully retrieved Feature Service: {service_name}")
        except Exception as service_error:
            logger.error(f"Feature Service retrieval failed: {service_error}")
            
            # Check for specific "not found" patterns in the error message
            error_str = str(service_error).lower()
            if any(phrase in error_str for phrase in ["not found", "does not exist", "not exist"]):
                workspace_name = config.workspace_name if config else "unknown"
                raise ValueError(
                    f"Feature Service '{service_name}' not found in workspace "
                    f"'{workspace_name}'. Please ensure the service name is "
                    f"correct and that the service exists in this workspace."
                )
            elif any(phrase in error_str for phrase in ["permission", "unauthorized", "access denied"]):
                raise ConnectionError(
                    f"Access denied to Feature Service '{service_name}'. Your API key "
                    f"may not have permission to access this service. Please contact "
                    f"your Tecton administrator."
                )
            else:
                # Unknown service-related error
                raise RuntimeError(
                    f"Failed to retrieve Feature Service '{service_name}'. This may "
                    f"indicate a configuration issue or Tecton service problem. "
                    f"Please try again or contact support. Details: {service_error}"
                )
        
        # Step 4.2: Fetch online features from the service
        try:
            logger.debug(f"Attempting to fetch online features from service: {service_name}")
            
            # Validate request_data is not None before passing
            safe_request_data = request_data if request_data is not None else {}
            
            feature_vector: FeatureVector = feature_service.get_online_features(
                join_keys=join_keys,
                request_data=safe_request_data
            )
            
            logger.debug(f"Successfully retrieved feature vector with {len(join_keys)} join keys")
            return feature_vector
            
        except Exception as features_error:
            logger.error(f"Feature retrieval failed: {features_error}")
            
            error_str = str(features_error).lower()
            
            # Authentication/Permission Errors
            if any(phrase in error_str for phrase in ["permission", "unauthorized", "access denied", "forbidden"]):
                raise ConnectionError(
                    f"Permission denied while fetching features from '{service_name}'. "
                    f"Your API key may lack the required permissions for this specific "
                    f"operation. Please contact your Tecton administrator."
                )
            
            # Invalid Argument Errors
            elif any(phrase in error_str for phrase in ["invalid", "malformed", "bad request", "400"]):
                raise ValueError(
                    f"Invalid request parameters for Feature Service '{service_name}'. "
                    f"Please check that your join_keys and request_data are properly "
                    f"formatted and contain valid values. Details: {features_error}"
                )
            
            # Rate Limiting or Quota Issues
            elif any(phrase in error_str for phrase in ["rate limit", "quota", "too many requests", "429"]):
                raise RuntimeError(
                    f"Rate limit exceeded for Feature Service '{service_name}'. "
                    f"Please wait before retrying or contact your Tecton administrator "
                    f"to increase your quota limits."
                )
            
            # Server/Network Errors
            elif any(phrase in error_str for phrase in ["server", "network", "timeout", "connection", "500", "502", "503", "504"]):
                raise RuntimeError(
                    f"Tecton's server returned an error while fetching features from "
                    f"'{service_name}'. This may be a transient issue. Please try again "
                    f"in a few moments. Server details: {features_error}"
                )
            
            # Step 4.3: The "Unknown Unknowns" Fallback
            else:
                raise RuntimeError(
                    f"An unexpected and unhandled error occurred while fetching "
                    f"features from '{service_name}'. This may indicate a change in "
                    f"the Tecton API, a network issue, or an unanticipated error "
                    f"condition. Please report this bug to your development team. "
                    f"Details: {features_error}"
                )