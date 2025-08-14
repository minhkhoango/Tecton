# Strict typing imports
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone

class MockSloInfo:
    """Mock SloInfo class that matches the expected interface."""
    def __init__(self, slo_eligible: bool, server_time_seconds: float, 
                 slo_server_time_seconds: float, store_response_time_seconds: float):
        self.slo_eligible = slo_eligible
        self.server_time_seconds = server_time_seconds
        self.slo_server_time_seconds = slo_server_time_seconds
        self.store_response_time_seconds = store_response_time_seconds

class MockFeatureVector:
    """Mock FeatureVector class that matches the expected interface."""
    def __init__(self, data: List[List[Any]], metadata: Dict[str, Any], slo_info: Optional[MockSloInfo]):
        self.data = data
        self.metadata = metadata
        self.slo_info = slo_info

    def to_dict(self, return_effective_times: bool = False) -> Dict[str, Any]:
        """Mock implementation of to_dict method to match Tecton SDK interface."""
        if return_effective_times:
            return {
                "__metadata__": self.metadata
            }
        else:
            return {k: v for k, v in self.data}

class MockTectonDebuggerClient:
    """
    A mock client that simulates responses from the Tecton SDK.

    This class is a stand-in for the real TectonDebuggerClient, allowing for
    demonstration and testing of the application without needing live credentials.
    It returns pre-canned data structures that mimic real FeatureVector objects.
    """
    def __init__(self) -> None:
        """No-op initializer as no connection is needed."""
        pass

    def _create_mock_feature_vector(
        self,
        features: Dict[str, Any],
        effective_times: Dict[str, str],
        slo_info: Optional[MockSloInfo]
    ) -> MockFeatureVector:
        """
        A helper method to construct a FeatureVector object from mock data.
        
        The Tecton SDK's FeatureVector is a complex object, so we instantiate it
        with the necessary components to ensure our analysis logic works correctly.
        """
        mock_data: List[List[Any]] = [[k, v] for k, v in features.items()]
        
        mock_metadata = {
            "features": [
                {"name": k, "dataType": {"type": "string"}} for k in features.keys()
            ],
            "effective_times": effective_times
        }
        
        return MockFeatureVector(data=mock_data, metadata=mock_metadata, slo_info=slo_info)

    def _create_green_scenario(self) -> MockFeatureVector:
        """Creates a mock response for a healthy, low-risk scenario."""
        now = datetime.now(timezone.utc)
        features = {
            "user_transaction_counts.transaction_count_7d": 15,
            "user_realtime_features.last_login_country": "US",
            "ad_hoc_feature.is_suspicious_ip": False,
        }
        effective_times = {
            "user_transaction_counts.transaction_count_7d": (now - timedelta(seconds=45)).isoformat().replace('+00:00', 'Z'),
            "user_realtime_features.last_login_country": (now - timedelta(seconds=10)).isoformat().replace('+00:00', 'Z'),
            "ad_hoc_feature.is_suspicious_ip": now.isoformat().replace('+00:00', 'Z'),
        }
        slo_info = MockSloInfo(
            slo_eligible=True,
            server_time_seconds=0.085,
            slo_server_time_seconds=0.1,
            store_response_time_seconds=0.05
        )
        return self._create_mock_feature_vector(features, effective_times, slo_info)

    def _create_yellow_scenario(self) -> MockFeatureVector:
        """Creates a mock response for a medium-risk scenario with stale data."""
        now = datetime.now(timezone.utc)
        features = {
            "user_profile_features.preferred_category": "electronics",
            "user_streaming_features.last_viewed_product_id": "prod_12345",
            "user_profile_features.is_premium_member": None,
        }
        effective_times = {
            "user_profile_features.preferred_category": (now - timedelta(minutes=35)).isoformat().replace('+00:00', 'Z'),
            "user_streaming_features.last_viewed_product_id": (now - timedelta(seconds=5)).isoformat().replace('+00:00', 'Z'),
            "user_profile_features.is_premium_member": (now - timedelta(minutes=35)).isoformat().replace('+00:00', 'Z'),
        }
        slo_info = MockSloInfo(
            slo_eligible=True,
            server_time_seconds=0.095,
            slo_server_time_seconds=0.1,
            store_response_time_seconds=0.06
        )
        return self._create_mock_feature_vector(features, effective_times, slo_info)

    def _create_red_scenario(self) -> MockFeatureVector:
        """Creates a mock response for a high-risk scenario with severe staleness."""
        now = datetime.now(timezone.utc)
        features = {
            "user_daily_batch_features.lifetime_value": 4500.75,
            "user_realtime_features.session_id": "session_xyz",
        }
        effective_times = {
            "user_daily_batch_features.lifetime_value": (now - timedelta(hours=2, minutes=30)).isoformat().replace('+00:00', 'Z'),
            "user_realtime_features.session_id": now.isoformat().replace('+00:00', 'Z'),
        }
        slo_info = MockSloInfo(
            slo_eligible=True,
            server_time_seconds=0.120,
            slo_server_time_seconds=0.1,
            store_response_time_seconds=0.08
        )
        return self._create_mock_feature_vector(features, effective_times, slo_info)

    def fetch_context_vector(
        self,
        service_name: str,
        join_keys: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None
    ) -> MockFeatureVector:
        """
        Returns a pre-canned mock FeatureVector based on the service name.
        This allows the demo to showcase different diagnostic results.
        """
        if "green" in service_name:
            return self._create_green_scenario()
        elif "yellow" in service_name:
            return self._create_yellow_scenario()
        elif "red" in service_name:
            return self._create_red_scenario()
        else:
            return self._create_green_scenario()