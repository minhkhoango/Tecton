# Strict typing imports
from typing import Dict, Any, Optional, List, Protocol
from enum import Enum
from dataclasses import dataclass
import hashlib
import random

class FeatureVectorProtocol(Protocol):
    """Protocol defining the interface that our mock needs to implement."""
    def to_dict(self) -> Dict[str, Any]: ...

class Quality(Enum):
    """Quality levels for mock scenarios."""
    GREEN = "Green"
    YELLOW = "Yellow"
    RED = "Red"
    REPETITIVE = "Repetitive"
    IRRELEVANT = "Irrelevant"
    FAIL = "Fail"

@dataclass(frozen=True)
class ChunkSpec:
    """Specification for a context chunk."""
    text: str
    score: float

@dataclass(frozen=True)
class Scenario:
    """Complete scenario with answer and chunks."""
    answer: str
    chunks: List[ChunkSpec]

class MockTectonDebuggerClient:
    """
    Mocks the retrieval of a RAG context vector from Tecton.
    
    This client simulates a Feature Service that has already performed a vector search
    based on the user's query and returns the resulting text chunks and their
    relevance scores as features.
    """
    
    def __init__(self):
        """Initialize the mock client with predefined scenarios."""
        self._scenarios = self._build_scenarios()
    
    def _build_scenarios(self) -> Dict[str, Dict[Quality, Scenario]]:
        """Build the scenario registry for all queries and qualities."""
        scenarios: Dict[str, Dict[Quality, Scenario]] = {}
        
        # Reset password scenarios
        scenarios["How do I reset my password?"] = {
            Quality.GREEN: Scenario(
                answer="Go to **Account Settings → Security → Reset Password**, or use **Forgot password**. 2FA required if enabled.",
                chunks=[
                    ChunkSpec("Go to Account Settings → Security and click Reset Password.", 0.86),
                    ChunkSpec("Use Forgot password on the login screen to receive an email link.", 0.84),
                    ChunkSpec("If 2FA is enabled, verify before setting a new password.", 0.80),
                ]
            ),
            Quality.YELLOW: Scenario(
                answer="Password policy: 12+ chars, rotate every 90 days.",
                chunks=[
                    ChunkSpec("Password policy: 12+ chars, rotate every 90 days.", 0.72),
                    ChunkSpec("Account locks after 5 failed attempts.", 0.68),
                ]
            ),
            Quality.RED: Scenario(
                answer="The login page is linked from the site header.",
                chunks=[
                    ChunkSpec("The login page is linked from the site header.", 0.58),
                    ChunkSpec("Our mission is to simplify security.", 0.52),
                ]
            ),
            Quality.IRRELEVANT: Scenario(
                answer="Pricing starts at $29/month for Basic.",
                chunks=[
                    ChunkSpec("Pricing starts at $29/month for Basic.", 0.45),
                    ChunkSpec("Support hours are Mon–Fri 9–5.", 0.38),
                ]
            ),
            Quality.REPETITIVE: Scenario(
                answer="To reset your password, open Account Settings → Security options.",
                chunks=[
                    ChunkSpec("To reset your password, open Account Settings → Security options.", 0.84),
                    ChunkSpec("To reset your password, open account settings → security options.", 0.83),
                    ChunkSpec("To reset your password, open the security options in account settings.", 0.82),
                ]
            ),
            Quality.FAIL: Scenario(
                answer="",
                chunks=[]
            ),
        }
        
        # SSO with Okta scenarios
        scenarios["How do I set up SSO with Okta?"] = {
            Quality.GREEN: Scenario(
                answer="Create SAML 2.0 app in Okta; set **ACS URL** & **Entity ID** from your SSO page; map **NameID=email**; assign users; enable in **Security → SSO**.",
                chunks=[
                    ChunkSpec("In Okta Admin, add SAML 2.0 app; set ACS URL and Entity ID from workspace SSO.", 0.88),
                    ChunkSpec("Map NameID=email and include firstName, lastName.", 0.84),
                    ChunkSpec("Assign users/groups; toggle Enable SSO in Security → SSO.", 0.81),
                ]
            ),
            Quality.YELLOW: Scenario(
                answer="Okta supports SAML/OpenID; many orgs use SAML.",
                chunks=[
                    ChunkSpec("Okta supports SAML/OpenID; many orgs use SAML.", 0.73),
                    ChunkSpec("Assign users in Okta to allow logins.", 0.67),
                ]
            ),
            Quality.RED: Scenario(
                answer="Dashboard shows active sessions.",
                chunks=[
                    ChunkSpec("Dashboard shows active sessions.", 0.59),
                    ChunkSpec("Use Reports for audit events.", 0.53),
                ]
            ),
            Quality.IRRELEVANT: Scenario(
                answer="Usage-based billing applies to API calls.",
                chunks=[
                    ChunkSpec("Usage-based billing applies to API calls.", 0.44),
                    ChunkSpec("Weekly release notes summarize UI tweaks.", 0.37),
                ]
            ),
            Quality.REPETITIVE: Scenario(
                answer="Create SAML app; set ACS URL & Entity ID.",
                chunks=[
                    ChunkSpec("Create SAML app; set ACS URL & Entity ID.", 0.85),
                    ChunkSpec("Create SAML app; set ACS URL & Entity ID.", 0.83),
                    ChunkSpec("Create SAML app; set ACS URL & Entity ID.", 0.82),
                ]
            ),
            Quality.FAIL: Scenario(
                answer="",
                chunks=[]
            ),
        }
        
        # Rotate API key scenarios
        scenarios["How do I rotate my API key?"] = {
            Quality.GREEN: Scenario(
                answer="**Developer Settings → API Keys** → **Generate new key**, update clients, then **Revoke** old key.",
                chunks=[
                    ChunkSpec("Open Developer Settings → API Keys and click Generate new key.", 0.87),
                    ChunkSpec("Deploy new key to all services; verify health checks.", 0.84),
                    ChunkSpec("Revoke the old key to prevent reuse.", 0.80),
                ]
            ),
            Quality.YELLOW: Scenario(
                answer="Send API key via Authorization header.",
                chunks=[
                    ChunkSpec("Send API key via Authorization header.", 0.71),
                    ChunkSpec("Keys are scoped to the workspace.", 0.66),
                ]
            ),
            Quality.RED: Scenario(
                answer="Regions include us-east and eu-central.",
                chunks=[
                    ChunkSpec("Regions include us-east and eu-central.", 0.58),
                    ChunkSpec("Data retention defaults to 30 days.", 0.52),
                ]
            ),
            Quality.IRRELEVANT: Scenario(
                answer="CLI supports interactive mode.",
                chunks=[
                    ChunkSpec("CLI supports interactive mode.", 0.46),
                    ChunkSpec("UI theme can be changed in Preferences.", 0.39),
                ]
            ),
            Quality.REPETITIVE: Scenario(
                answer="Generate new key in Developer Settings.",
                chunks=[
                    ChunkSpec("Generate new key in Developer Settings.", 0.85),
                    ChunkSpec("Generate new key in Developer Settings.", 0.83),
                    ChunkSpec("Generate new key in Developer Settings.", 0.82),
                ]
            ),
            Quality.FAIL: Scenario(
                answer="",
                chunks=[]
            ),
        }
        
        return scenarios

    def _derive_seed(self, query: str, quality: Quality, seed: Optional[int]) -> int:
        """Derive a deterministic seed from query and quality, or use provided seed."""
        if seed is not None:
            return seed
        
        # Create deterministic hash from query and quality
        hash_input = f"{query}|{quality.value}".encode()
        hash_hex = hashlib.sha256(hash_input).hexdigest()
        return int(hash_hex[:8], 16)

    def _jitter(self, chunks: List[ChunkSpec], seed: int) -> List[ChunkSpec]:
        """Apply ±0.02 jitter to chunk scores using deterministic random seed."""
        rng = random.Random(seed)
        jittered_chunks: List[ChunkSpec] = []
        
        for chunk in chunks:
            # Add jitter and clip to [0, 1] range
            jittered_score = max(0.0, min(1.0, chunk.score + rng.uniform(-0.02, 0.02)))
            jittered_chunks.append(ChunkSpec(chunk.text, jittered_score))
        
        return jittered_chunks

    def _create_mock_feature_vector(self, features: Dict[str, Any]) -> FeatureVectorProtocol:
        """Helper to construct a mock FeatureVector object from a simple dictionary."""
        # Create a mock FeatureVector that implements the required interface
        class MockFeatureVector:
            def __init__(self, features_dict: Dict[str, Any]):
                self._features = features_dict
            
            def to_dict(self) -> Dict[str, Any]:
                return self._features
        
        return MockFeatureVector(features)

    def fetch_context_vector(
        self,
        service_name: str,
        join_keys: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None
    ) -> FeatureVectorProtocol:
        """Returns a mock FeatureVector based on the service_name parameter and query."""
        # Default values
        default_query = "How do I reset my password?"
        query = request_data.get("query", default_query) if request_data else default_query
        seed = request_data.get("seed") if request_data else None
        
        # Interpret service_name as quality (case-insensitive)
        try:
            quality = Quality(service_name)
        except ValueError:
            # Default to GREEN for unknown service names
            quality = Quality.GREEN
        
        # Get scenario for this query and quality
        if query not in self._scenarios:
            query = default_query  # Fallback to default query
        
        scenario = self._scenarios[query][quality]
        
        # Apply jitter with derived seed
        jittered_chunks = self._jitter(scenario.chunks, self._derive_seed(query, quality, seed))
        
        # Calculate post-jitter average score
        if jittered_chunks:
            avg_score = sum(chunk.score for chunk in jittered_chunks) / len(jittered_chunks)
        else:
            avg_score = 0.0
        
        # Build features dictionary
        features: Dict[str, Any] = {}
        
        # Add chunk features (1-indexed)
        for i, chunk in enumerate(jittered_chunks, 1):
            features[f"retrieved_context.chunk_{i}_text"] = chunk.text
            features[f"retrieved_context.chunk_{i}_score"] = chunk.score
        
        # Add answer surface features
        features["retrieved_context.answer"] = scenario.answer
        features["retrieved_context.answer_confidence"] = avg_score
        
        return self._create_mock_feature_vector(features)