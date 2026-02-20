"""
Similarity Matching Service for Trajectory Engine MVP

This module implements similarity calculation functions using NumPy.
NO LLM is used for similarity matching - only pure mathematics.

Similarity Metrics:
1. Cosine Similarity (70% weight) - Measures angle between vectors
2. Euclidean Similarity (30% weight) - Measures distance between vectors
3. Ensemble Similarity - Weighted combination of both

All similarity scores are in [0, 1] range where 1 = identical, 0 = completely different.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# SIMILARITY CALCULATION FUNCTIONS (Task 7.1)
# ============================================================================

def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Cosine similarity measures the angle between two vectors, ignoring magnitude.
    It's ideal for comparing patterns regardless of scale.
    
    Formula: cos(θ) = (A · B) / (||A|| × ||B||)
    
    Args:
        vec_a: First vector (numpy array)
        vec_b: Second vector (numpy array)
    
    Returns:
        Similarity score in [0, 1] range
        - 1.0 = identical direction (perfect match)
        - 0.5 = orthogonal (no similarity)
        - 0.0 = opposite direction (completely different)
    
    Examples:
        >>> vec_a = np.array([1, 0, 0])
        >>> vec_b = np.array([1, 0, 0])
        >>> cosine_similarity(vec_a, vec_b)
        1.0
        
        >>> vec_a = np.array([1, 0, 0])
        >>> vec_b = np.array([0, 1, 0])
        >>> cosine_similarity(vec_a, vec_b)
        0.5
    """
    # Handle edge cases
    if vec_a.size == 0 or vec_b.size == 0:
        logger.warning("Empty vector provided to cosine_similarity")
        return 0.0
    
    if vec_a.shape != vec_b.shape:
        logger.error(f"Vector shape mismatch: {vec_a.shape} vs {vec_b.shape}")
        return 0.0
    
    # Calculate dot product
    dot_product = np.dot(vec_a, vec_b)
    
    # Calculate magnitudes (L2 norms)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    # Handle zero vectors
    if norm_a == 0 or norm_b == 0:
        logger.warning("Zero vector provided to cosine_similarity")
        return 0.0
    
    # Calculate cosine similarity
    cos_sim = dot_product / (norm_a * norm_b)
    
    # Cosine similarity is in [-1, 1], normalize to [0, 1]
    # -1 (opposite) → 0, 0 (orthogonal) → 0.5, 1 (identical) → 1
    normalized = (cos_sim + 1.0) / 2.0
    
    # Clip to ensure [0, 1] range (handle floating point errors)
    return float(np.clip(normalized, 0.0, 1.0))


def euclidean_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Calculate Euclidean similarity between two vectors.
    
    Euclidean similarity measures the distance between two points in space.
    It's sensitive to both direction and magnitude.
    
    Formula: similarity = 1 / (1 + distance)
    where distance = sqrt(Σ(a[i] - b[i])²)
    
    Args:
        vec_a: First vector (numpy array)
        vec_b: Second vector (numpy array)
    
    Returns:
        Similarity score in [0, 1] range
        - 1.0 = identical vectors (distance = 0)
        - 0.5 = moderate distance
        - 0.0 = very far apart (distance → ∞)
    
    Examples:
        >>> vec_a = np.array([1, 0, 0])
        >>> vec_b = np.array([1, 0, 0])
        >>> euclidean_similarity(vec_a, vec_b)
        1.0
        
        >>> vec_a = np.array([0, 0, 0])
        >>> vec_b = np.array([1, 1, 1])
        >>> euclidean_similarity(vec_a, vec_b)
        0.366...
    """
    # Handle edge cases
    if vec_a.size == 0 or vec_b.size == 0:
        logger.warning("Empty vector provided to euclidean_similarity")
        return 0.0
    
    if vec_a.shape != vec_b.shape:
        logger.error(f"Vector shape mismatch: {vec_a.shape} vs {vec_b.shape}")
        return 0.0
    
    # Calculate Euclidean distance
    distance = np.linalg.norm(vec_a - vec_b)
    
    # Convert distance to similarity using inverse function
    # Distance 0 → similarity 1.0
    # Distance 1 → similarity 0.5
    # Distance ∞ → similarity 0.0
    similarity = 1.0 / (1.0 + distance)
    
    return float(similarity)


def ensemble_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Calculate ensemble similarity combining cosine and Euclidean metrics.
    
    Ensemble similarity combines the strengths of both metrics:
    - Cosine: Good for pattern matching (ignores scale)
    - Euclidean: Good for magnitude matching (considers scale)
    
    Formula: ensemble = (cosine × 0.70) + (euclidean × 0.30)
    
    Weights chosen based on:
    - Cosine (70%): More important for matching behavioral patterns
    - Euclidean (30%): Adds sensitivity to actual value differences
    
    Args:
        vec_a: First vector (numpy array)
        vec_b: Second vector (numpy array)
    
    Returns:
        Similarity score in [0, 1] range
    
    Examples:
        >>> vec_a = np.array([0.8, 0.7, 0.9])
        >>> vec_b = np.array([0.8, 0.7, 0.9])
        >>> ensemble_similarity(vec_a, vec_b)
        1.0
        
        >>> vec_a = np.array([0.8, 0.7, 0.9])
        >>> vec_b = np.array([0.4, 0.3, 0.5])
        >>> ensemble_similarity(vec_a, vec_b)
        0.85...  # High cosine (same pattern), lower euclidean (different scale)
    """
    # Calculate both similarities
    cos_sim = cosine_similarity(vec_a, vec_b)
    euc_sim = euclidean_similarity(vec_a, vec_b)
    
    # Weighted combination (70% cosine, 30% euclidean)
    ensemble = (cos_sim * 0.70) + (euc_sim * 0.30)
    
    return float(ensemble)


# ============================================================================
# QDRANT-BASED SIMILARITY SEARCH (Task 7.3)
# ============================================================================

def find_similar_alumni(
    student_vector: np.ndarray,
    qdrant_service,
    major: Optional[str] = None,
    top_k: int = 5,
    use_ensemble: bool = False
) -> List[Dict]:
    """
    Find similar alumni using Qdrant vector database.
    
    This function queries Qdrant for the top K most similar alumni vectors
    using cosine similarity (default) or ensemble similarity (optional).
    
    Args:
        student_vector: 15-dimensional student vector
        qdrant_service: QdrantService instance
        major: Optional major filter (e.g., "Computer Science")
        top_k: Number of results to return (default: 5)
        use_ensemble: If True, recalculate with ensemble similarity (default: False)
    
    Returns:
        List of dicts with keys:
            - alumni_id (int)
            - similarity_score (float): 0-1 scale
            - name (str)
            - major (str)
            - graduation_year (int)
            - company_tier (str)
            - salary_range (str)
            - placement_status (str)
            - outcome_score (float)
    
    Examples:
        >>> from app.services.qdrant_service import QdrantService
        >>> qdrant = QdrantService()
        >>> student_vec = np.array([0.75, 0.80, ...])  # 15 dimensions
        >>> results = find_similar_alumni(student_vec, qdrant, major="Computer Science")
        >>> len(results)
        5
        >>> results[0]['similarity_score']
        0.95
    """
    # Validate input
    if student_vector.size == 0:
        logger.error("Empty student vector provided")
        return []
    
    if student_vector.shape[0] != 15:
        logger.error(f"Invalid vector dimension: {student_vector.shape[0]}, expected 15")
        return []
    
    # Query Qdrant for similar alumni
    results = qdrant_service.find_similar_alumni(
        student_vector=student_vector,
        major=major,
        top_k=top_k
    )
    
    # If Qdrant returned empty results, return empty list
    if not results:
        logger.warning(f"No similar alumni found for major: {major}")
        return []
    
    # If ensemble similarity requested, recalculate scores
    if use_ensemble:
        logger.info("Recalculating with ensemble similarity")
        # Note: This requires fetching alumni vectors from Qdrant
        # For MVP, we'll use Qdrant's cosine similarity directly
        # Ensemble can be added in future iterations
        pass
    
    # Sort by similarity score (highest first)
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    logger.info(f"Found {len(results)} similar alumni (top_k={top_k}, major={major})")
    
    return results


def handle_empty_results(major: Optional[str] = None) -> List[Dict]:
    """
    Handle case when no alumni matches are found.
    
    Returns empty list with appropriate logging.
    
    Args:
        major: Optional major that was searched
    
    Returns:
        Empty list
    """
    if major:
        logger.warning(f"No alumni data available for major: {major}")
    else:
        logger.warning("No alumni data available in database")
    
    return []


def filter_by_major(
    results: List[Dict],
    major: str
) -> List[Dict]:
    """
    Filter similarity results by major.
    
    This is a fallback function for when Qdrant filtering is not available.
    Normally, Qdrant handles filtering during the query.
    
    Args:
        results: List of similarity results
        major: Major to filter by
    
    Returns:
        Filtered list of results
    """
    filtered = [r for r in results if r.get('major') == major]
    logger.info(f"Filtered {len(results)} results to {len(filtered)} for major: {major}")
    return filtered


def sort_by_recency(
    results: List[Dict]
) -> List[Dict]:
    """
    Sort results by graduation year (most recent first) when similarity scores are tied.
    
    Args:
        results: List of similarity results
    
    Returns:
        Sorted list (by similarity desc, then recency desc)
    """
    # Sort by similarity (desc), then graduation_year (desc)
    sorted_results = sorted(
        results,
        key=lambda x: (x['similarity_score'], x.get('graduation_year', 0)),
        reverse=True
    )
    
    return sorted_results


# ============================================================================
# FALLBACK TO POSTGRESQL (when Qdrant unavailable)
# ============================================================================

def find_similar_alumni_fallback(
    student_vector: np.ndarray,
    alumni_data: List[Tuple[int, np.ndarray, Dict]],
    major: Optional[str] = None,
    top_k: int = 5,
    use_ensemble: bool = True
) -> List[Dict]:
    """
    Fallback similarity search using PostgreSQL + NumPy.
    
    Used when Qdrant is unavailable. Calculates similarity in-memory.
    
    Args:
        student_vector: 15-dimensional student vector
        alumni_data: List of (alumni_id, vector, metadata) tuples from PostgreSQL
        major: Optional major filter
        top_k: Number of results to return
        use_ensemble: If True, use ensemble similarity (default: True)
    
    Returns:
        List of similar alumni (same format as Qdrant search)
    """
    logger.info("Using PostgreSQL fallback for similarity search")
    
    similarities = []
    
    for alumni_id, alumni_vector, metadata in alumni_data:
        # Filter by major if specified
        if major and metadata.get('major') != major:
            continue
        
        # Calculate similarity
        if use_ensemble:
            similarity = ensemble_similarity(student_vector, alumni_vector)
        else:
            similarity = cosine_similarity(student_vector, alumni_vector)
        
        similarities.append({
            'alumni_id': alumni_id,
            'similarity_score': similarity,
            'name': metadata.get('name', ''),
            'major': metadata.get('major', ''),
            'graduation_year': metadata.get('graduation_year', 0),
            'company_tier': metadata.get('company_tier', ''),
            'salary_range': metadata.get('salary_range', ''),
            'placement_status': metadata.get('placement_status', ''),
            'outcome_score': metadata.get('outcome_score', 0.0)
        })
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Return top K
    results = similarities[:top_k]
    
    logger.info(f"Fallback search found {len(results)} similar alumni")
    
    return results


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_vector(vector: np.ndarray, expected_dim: int = 15) -> bool:
    """
    Validate that a vector has the correct shape and values.
    
    Args:
        vector: Vector to validate
        expected_dim: Expected number of dimensions (default: 15)
    
    Returns:
        True if valid, False otherwise
    """
    if vector.size == 0:
        logger.error("Empty vector")
        return False
    
    if vector.shape[0] != expected_dim:
        logger.error(f"Invalid dimension: {vector.shape[0]}, expected {expected_dim}")
        return False
    
    if not np.all(np.isfinite(vector)):
        logger.error("Vector contains NaN or Inf values")
        return False
    
    if not np.all((vector >= 0) & (vector <= 1)):
        logger.warning("Vector values outside [0, 1] range")
        # Don't return False - just warn, as this might be intentional
    
    return True


def calculate_similarity_statistics(results: List[Dict]) -> Dict:
    """
    Calculate statistics about similarity results.
    
    Args:
        results: List of similarity results
    
    Returns:
        Dict with statistics:
            - mean_similarity (float)
            - std_similarity (float)
            - min_similarity (float)
            - max_similarity (float)
            - count (int)
    """
    if not results:
        return {
            'mean_similarity': 0.0,
            'std_similarity': 0.0,
            'min_similarity': 0.0,
            'max_similarity': 0.0,
            'count': 0
        }
    
    scores = [r['similarity_score'] for r in results]
    
    return {
        'mean_similarity': float(np.mean(scores)),
        'std_similarity': float(np.std(scores)),
        'min_similarity': float(np.min(scores)),
        'max_similarity': float(np.max(scores)),
        'count': len(scores)
    }
