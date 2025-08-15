# Strict typing imports
from typing import Dict, Any, Optional, Protocol

class FeatureVectorProtocol(Protocol):
    """Protocol defining the interface that our mock needs to implement."""
    def to_dict(self) -> Dict[str, Any]: ...

class MockTectonDebuggerClient:
    """
    Mocks the retrieval of a RAG context vector from Tecton.
    
    This client simulates a Feature Service that has already performed a vector search
    based on the user's query and returns the resulting text chunks and their
    relevance scores as features.
    """
    def _create_mock_feature_vector(self, features: Dict[str, Any]) -> FeatureVectorProtocol:
        """Helper to construct a mock FeatureVector object from a simple dictionary."""
        # Create a mock FeatureVector that implements the required interface
        class MockFeatureVector:
            def __init__(self, features_dict: Dict[str, Any]):
                self._features = features_dict
            
            def to_dict(self) -> Dict[str, Any]:
                return self._features
        
        return MockFeatureVector(features)

    def _get_green_context(self) -> FeatureVectorProtocol:
        """Simulates a good, healthy retrieval with relevant and diverse chunks."""
        features = {
            "retrieved_context.chunk_1_text": "To reset your password, navigate to the Account Settings page and click 'Security'.",
            "retrieved_context.chunk_1_score": 0.92,
            "retrieved_context.chunk_2_text": "If you have forgotten your password, you can use the 'Forgot Password' link on the login page.",
            "retrieved_context.chunk_2_score": 0.88,
            "retrieved_context.chunk_3_text": "Two-factor authentication (2FA) is required for all password resets for added security.",
            "retrieved_context.chunk_3_score": 0.85,
        }
        return self._create_mock_feature_vector(features)

    def _get_yellow_context(self) -> FeatureVectorProtocol:
        """Simulates a response with mediocre relevance (WARNING status)."""
        features = {
            "retrieved_context.chunk_1_text": "To reset your password, navigate to the Account Settings page and click 'Security'.",
            "retrieved_context.chunk_1_score": 0.78,  # Below 0.82 threshold for WARNING
            "retrieved_context.chunk_2_text": "If you have forgotten your password, you can use the 'Forgot Password' link on the login page.",
            "retrieved_context.chunk_2_score": 0.75,  # Below 0.82 threshold for WARNING
            "retrieved_context.chunk_3_text": None,  # Simulate null value
            "retrieved_context.chunk_3_score": 0.0,
        }
        return self._create_mock_feature_vector(features)

    def _get_red_context(self) -> FeatureVectorProtocol:
        """Simulates a response with poor relevance scores (CRITICAL status)."""
        features = {
            "retrieved_context.chunk_1_text": "Our company was founded in 2015 with a mission to improve security.",
            "retrieved_context.chunk_1_score": 0.65,  # Below 0.75 threshold for CRITICAL
            "retrieved_context.chunk_2_text": "The login page can be accessed from the main homepage.",
            "retrieved_context.chunk_2_score": 0.61,  # Below 0.75 threshold for CRITICAL
        }
        return self._create_mock_feature_vector(features)

    def _get_irrelevant_context(self) -> FeatureVectorProtocol:
        """Simulates a retrieval where the chunks are a poor match for the query (CRITICAL status)."""
        features = {
            "retrieved_context.chunk_1_text": "Our company was founded in 2015 with a mission to improve security.",
            "retrieved_context.chunk_1_score": 0.65, # Low score
            "retrieved_context.chunk_2_text": "The login page can be accessed from the main homepage.",
            "retrieved_context.chunk_2_score": 0.61, # Low score
        }
        return self._create_mock_feature_vector(features)

    def _get_repetitive_context(self) -> FeatureVectorProtocol:
        """Simulates a retrieval where the chunks are highly repetitive (WARNING status) - should produce ~0.79 diversity."""
        features = {
            "retrieved_context.chunk_1_text": "To reset your password, go to Account Settings and find the security options.",
            "retrieved_context.chunk_1_score": 0.91,
            "retrieved_context.chunk_2_text": "To reset your password, go to Account Settings and find the security options.",
            "retrieved_context.chunk_2_score": 0.90,
            "retrieved_context.chunk_3_text": "To reset your password, go to Account Settings and find the security options.",
            "retrieved_context.chunk_3_score": 0.89,
        }
        return self._create_mock_feature_vector(features)
        
    def _get_fail_context(self) -> FeatureVectorProtocol:
        """Simulates a failed retrieval with no context found (CRITICAL status)."""
        return self._create_mock_feature_vector({})

    def fetch_context_vector(
        self,
        service_name: str,
        join_keys: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None
    ) -> FeatureVectorProtocol:
        """Returns a mock FeatureVector based on the service_name parameter."""
        service_name_lower = service_name.lower()

        if "green" in service_name_lower:
            return self._get_green_context()
        elif "yellow" in service_name_lower:
            return self._get_yellow_context()
        elif "red" in service_name_lower:
            return self._get_red_context()
        elif "irrelevant" in service_name_lower:
            return self._get_irrelevant_context()
        elif "repetitive" in service_name_lower:
            return self._get_repetitive_context()
        elif "fail" in service_name_lower:
            return self._get_fail_context()
        else:
            # Default to green context for any other service name
            return self._get_green_context()