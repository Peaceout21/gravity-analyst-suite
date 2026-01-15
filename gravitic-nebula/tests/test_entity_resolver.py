import numpy as np
import pytest
from core.entity_resolver.engine import HybridResolver

# Golden Dataset: Messy Inputs -> Expected Canonical
GOLDEN_DATA = [
    ("Hon Hai Precision Ind. Co.", "Foxconn"),
    ("Apple Computer Inc.", "Apple Inc."),
    ("Alphabet Class C", "Alphabet Inc."),
    ("Space Exploration Corp", "SpaceX"), # Semantic check
    ("Taiwan Semiconductor Mfg.", "TSMC")
]

KNOWN_ENTITIES = [
    {"name": "Foxconn", "ticker": "2317.TW", "aliases": ["Hon Hai Precision Ind. Co.", "Hon Hai"]},
    {"name": "Apple Inc.", "ticker": "AAPL", "aliases": ["Apple Computer"]},
    {"name": "Alphabet Inc.", "ticker": "GOOG", "aliases": ["Google"]},
    {"name": "SpaceX", "ticker": "PRIVATE:SPACE", "aliases": ["Space Exploration Technologies Corp", "Space Exploration Corp"]},
    {"name": "TSMC", "ticker": "TSM", "aliases": ["Taiwan Semiconductor Mfg."]}
]

class DummyVectorModel:
    def encode(self, inputs, convert_to_tensor=True):
        if isinstance(inputs, list):
            return np.array([self._vector(text) for text in inputs])
        return np.array(self._vector(inputs))

    def _vector(self, text):
        base = text.lower()
        if "space" in base:
            return [1.0, 0.0, 0.0, 0.0]
        if "hon hai" in base or "foxconn" in base:
            return [0.0, 1.0, 0.0, 0.0]
        if "apple" in base:
            return [0.0, 0.0, 1.0, 0.0]
        if "alphabet" in base or "google" in base:
            return [0.0, 0.0, 0.0, 1.0]
        if "tsmc" in base or "taiwan" in base:
            return [0.5, 0.5, 0.0, 0.0]
        return [0.0, 0.0, 0.0, 0.0]


def dummy_cos_sim(query_vec, matrix):
    query = np.array(query_vec)
    mat = np.array(matrix)
    if query.ndim == 1:
        query = query.reshape(1, -1)
    scores = np.dot(query, mat.T)
    return scores


@pytest.fixture(scope="module")
def resolver():
    print("Initializing HybridResolver...")
    r = HybridResolver(
        vector_model=DummyVectorModel(),
        similarity_fn=dummy_cos_sim,
    )
    r.load_entities(KNOWN_ENTITIES)
    return r

@pytest.mark.parametrize("query,expected_name", GOLDEN_DATA)
def test_resolution_accuracy(resolver, query, expected_name):
    result = resolver.resolve(query)
    
    assert result is not None, f"Failed to resolve '{query}'"
    assert result['canonical_name'] == expected_name
    print(f"✅ Resolved '{query}' -> {result['canonical_name']} ({result['confidence']:.2f})")

def test_no_match(resolver):
    # Garbage input should return None or low confidence
    result = resolver.resolve("Pizza Hut Generative AI")
    # Note: If it matches something, it should have low confidence. 
    # With MiniLM, unrelated things usually score < 0.2
    if result:
        assert result['confidence'] < 0.3, "False positive confidence too high"
