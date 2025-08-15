from typing import Dict, Any, List, TypedDict, Optional

# Import our protocol for type compatibility
from .mock_client import FeatureVectorProtocol

# Using TypedDict for well-defined, type-checked dictionary structures.
# This makes the data flow between modules much safer and easier to reason about.

class RetrievedChunk(TypedDict):
    text: str
    score: float

class ContextHealthReport(TypedDict):
    status: str
    message: str
    chunk_count: int
    avg_relevance_score: float
    semantic_diversity_score: float

class AnalysisResult(TypedDict, total=False):
    retrieved_chunks: List[RetrievedChunk]
    health_report: ContextHealthReport
    error: Optional[str]
    generated_answer: str
    answer_confidence: float

def _extract_chunks(fv_object: FeatureVectorProtocol) -> List[RetrievedChunk]:
    """Extract and parse retrieved context chunks from the feature vector."""
    features = fv_object.to_dict()
    chunks: Dict[int, Dict[str, Any]] = {}
    
    for key, value in features.items():
        # Handle both dot notation (retrieved_context.chunk_1_text) and underscore notation (chunk_1_text)
        if "chunk" in key and ("text" in key or "score" in key):
            try:
                # Split by both dot and underscore to handle different formats
                if '.' in key:
                    # Handle dot notation: retrieved_context.chunk_1_text
                    parts = key.split('.')
                    chunk_part = parts[1] if len(parts) > 1 else key
                else:
                    # Handle underscore notation: chunk_1_text
                    chunk_part = key
                
                # Extract chunk number from chunk_1_text or similar
                chunk_parts = chunk_part.split('_')
                if len(chunk_parts) >= 2 and chunk_parts[0] == 'chunk':
                    chunk_num = int(chunk_parts[1])
                    if chunk_num not in chunks:
                        chunks[chunk_num] = {}
                    
                    # Store text and score separately - check the end of the key
                    if key.endswith('_text'):
                        # Skip null values
                        if value is not None:
                            chunks[chunk_num]['text'] = str(value)
                    elif key.endswith('_score'):
                        # Skip null values
                        if value is not None:
                            chunks[chunk_num]['score'] = float(value)
            except (ValueError, IndexError):
                continue
    
    # Sort chunks by number and filter out incomplete ones
    sorted_chunks = sorted(chunks.items())
    result: List[RetrievedChunk] = [
        {"text": chunk_data['text'], "score": chunk_data['score']} 
        for _, chunk_data in sorted_chunks 
        if 'text' in chunk_data and 'score' in chunk_data
    ]
    return result

def _calculate_semantic_diversity(texts: List[str]) -> float:
    """Calculate a simple semantic diversity score based on text similarity."""
    if len(texts) < 2:
        return 1.0  # Single chunk is considered diverse
    
    # Simple heuristic: check for repeated phrases and word overlap
    all_words: set[str] = set()
    total_words = 0
    repeated_phrases = 0
    phrase_similarity_score = 0
    
    for text in texts:
        words = text.lower().split()
        total_words += len(words)
        all_words.update(words)
        
        # Check for repeated phrases and high similarity
        for other_text in texts:
            if text != other_text:
                # Check if one text is contained in another (strong repetition)
                if text.lower() in other_text.lower() or other_text.lower() in text.lower():
                    repeated_phrases += 1
                
                # Calculate word overlap between texts
                other_words = set(other_text.lower().split())
                overlap = len(set(words) & other_words)
                total_unique = len(set(words) | other_words)
                if total_unique > 0:
                    similarity = overlap / total_unique
                    phrase_similarity_score += similarity
    
    # Calculate diversity based on unique words and phrase repetition
    word_diversity = len(all_words) / max(total_words, 1)
    
    # Normalize phrase similarity score
    max_possible_similarity = len(texts) * (len(texts) - 1)
    if max_possible_similarity > 0:
        phrase_similarity_score = phrase_similarity_score / max_possible_similarity
        phrase_diversity = max(0, 1 - phrase_similarity_score)
    else:
        phrase_diversity = 1.0
    
    # Penalize heavily for repeated phrases
    phrase_penalty = max(0, repeated_phrases / max(len(texts) * (len(texts) - 1), 1))
    phrase_diversity = phrase_diversity * (1 - phrase_penalty)
    
    # Combine both metrics with more weight on phrase diversity for context collapse detection
    return (word_diversity * 0.3 + phrase_diversity * 0.7)

def analyze_retrieved_context(fv_object: FeatureVectorProtocol | None) -> AnalysisResult:
    """
    Analyzes a retrieved context vector and provides health diagnostics.
    
    Args:
        fv_object: The FeatureVector object returned by the Tecton SDK or mock client.
        
    Returns:
        An AnalysisResult dictionary containing the context health diagnosis.
    """
    if fv_object is None:
        # Return a structure consistent with a failed analysis
        failed_health_report: ContextHealthReport = {
            "status": "CRITICAL", 
            "message": "Received null feature vector.", 
            "chunk_count": 0, 
            "avg_relevance_score": 0.0, 
            "semantic_diversity_score": 0.0
        }
        return {
            "retrieved_chunks": [], 
            "health_report": failed_health_report, 
            "error": "Received null feature vector."
        }

    # Extract chunks from the feature vector
    chunks = _extract_chunks(fv_object)
    chunk_count = len(chunks)
    
    # Extract answer surface features
    features = fv_object.to_dict()
    generated_answer = features.get("retrieved_context.answer", "")
    answer_confidence = features.get("retrieved_context.answer_confidence")
    
    if chunk_count == 0:
        empty_health_report: ContextHealthReport = {
            "status": "CRITICAL", 
            "message": "No context chunks retrieved.", 
            "chunk_count": 0, 
            "avg_relevance_score": 0.0, 
            "semantic_diversity_score": 0.0
        }
        return {
            "retrieved_chunks": [], 
            "health_report": empty_health_report, 
            "error": None,
            "generated_answer": generated_answer,
            "answer_confidence": answer_confidence if answer_confidence is not None else 0.0
        }

    # Calculate metrics
    scores = [chunk['score'] for chunk in chunks]
    texts = [chunk['text'] for chunk in chunks]
    avg_score = sum(scores) / chunk_count
    diversity_score = _calculate_semantic_diversity(texts)
    
    # Determine health status
    status = "HEALTHY"
    message = "GOOD: The chunks answer the user's question well and provide different useful information."
    
    if avg_score < 0.60:
        status = "CRITICAL"
        message = "BAD: The chunks don't answer the user's question well. They're off-topic."
    elif avg_score < 0.75:
        status = "WARNING"
        message = "WARNING: The chunks only kinda answer the user's question. They're not very helpful."
        
    if diversity_score < 0.80 and status != "CRITICAL":
        status = "WARNING"
        message = "WARNING: The chunks are too similar to each other. They're basically saying the same thing."

    final_health_report: ContextHealthReport = {
        "status": status, 
        "message": message, 
        "chunk_count": chunk_count,
        "avg_relevance_score": avg_score, 
        "semantic_diversity_score": diversity_score
    }

    return {
        "retrieved_chunks": chunks, 
        "health_report": final_health_report, 
        "error": None,
        "generated_answer": generated_answer,
        "answer_confidence": answer_confidence if answer_confidence is not None else avg_score
    }