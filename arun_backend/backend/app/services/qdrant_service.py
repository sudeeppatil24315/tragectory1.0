"""
Qdrant Vector Database Service for Trajectory Engine MVP

This module handles all interactions with Qdrant vector database:
- Collection creation and management
- Vector storage and updates
- Similarity search queries
- Fallback to PostgreSQL if Qdrant unavailable

Qdrant is used for fast similarity search using HNSW index.
PostgreSQL is the source of truth for profile data.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams
)
from qdrant_client.http import models
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class QdrantService:
    """
    Service for managing Qdrant vector database operations.
    
    Collections:
    - students: Current student vectors (15 dimensions)
    - alumni: Historical alumni vectors (15 dimensions)
    
    Both collections use cosine similarity for matching.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        Initialize Qdrant client.
        
        Args:
            host: Qdrant server host (default: localhost)
            port: Qdrant server port (default: 6333)
        """
        try:
            self.client = QdrantClient(host=host, port=port)
            self.is_available = True
            logger.info(f"Connected to Qdrant at {host}:{port}")
        except Exception as e:
            self.client = None
            self.is_available = False
            logger.warning(f"Qdrant unavailable: {e}. Will use PostgreSQL fallback.")
    
    def create_collections(self, vector_size: int = 15):
        """
        Create students and alumni collections if they don't exist.
        
        Args:
            vector_size: Dimension of vectors (default: 15)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("Qdrant unavailable. Cannot create collections.")
            return False
        
        try:
            # Create students collection
            if not self.client.collection_exists("students"):
                self.client.create_collection(
                    collection_name="students",
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info("Created 'students' collection")
            
            # Create alumni collection
            if not self.client.collection_exists("alumni"):
                self.client.create_collection(
                    collection_name="alumni",
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info("Created 'alumni' collection")
            
            return True
        
        except Exception as e:
            logger.error(f"Error creating collections: {e}")
            return False
    
    def store_student_vector(
        self,
        student_id: int,
        vector: np.ndarray,
        metadata: Dict
    ) -> bool:
        """
        Store student vector in Qdrant.
        
        Args:
            student_id: Unique student ID
            vector: 15-dimensional numpy array
            metadata: Dictionary with student info:
                - name (str)
                - major (str)
                - semester (int)
                - gpa (float)
                - attendance (float)
                - trajectory_score (float, optional)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("Qdrant unavailable. Cannot store student vector.")
            return False
        
        try:
            # Ensure collection exists
            if not self.client.collection_exists("students"):
                self.create_collections()
            
            # Convert numpy array to list
            vector_list = vector.tolist() if isinstance(vector, np.ndarray) else vector
            
            # Create point with metadata
            point = PointStruct(
                id=student_id,
                vector=vector_list,
                payload={
                    "student_id": student_id,
                    "name": metadata.get("name", ""),
                    "major": metadata.get("major", ""),
                    "semester": metadata.get("semester", 0),
                    "gpa": float(metadata.get("gpa", 0.0)),
                    "attendance": float(metadata.get("attendance", 0.0)),
                    "trajectory_score": float(metadata.get("trajectory_score", 0.0)),
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            # Upsert point (insert or update)
            self.client.upsert(
                collection_name="students",
                points=[point]
            )
            
            logger.info(f"Stored vector for student {student_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error storing student vector: {e}")
            return False
    
    def store_alumni_vector(
        self,
        alumni_id: int,
        vector: np.ndarray,
        metadata: Dict
    ) -> bool:
        """
        Store alumni vector in Qdrant.
        
        Args:
            alumni_id: Unique alumni ID
            vector: 15-dimensional numpy array
            metadata: Dictionary with alumni info:
                - name (str)
                - major (str)
                - graduation_year (int)
                - company_tier (str): Tier1, Tier2, Tier3
                - salary_range (str)
                - placement_status (str): Placed, Not Placed
                - outcome_score (float): 0-100
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("Qdrant unavailable. Cannot store alumni vector.")
            return False
        
        try:
            # Ensure collection exists
            if not self.client.collection_exists("alumni"):
                self.create_collections()
            
            # Convert numpy array to list
            vector_list = vector.tolist() if isinstance(vector, np.ndarray) else vector
            
            # Create point with metadata
            point = PointStruct(
                id=alumni_id,
                vector=vector_list,
                payload={
                    "alumni_id": alumni_id,
                    "name": metadata.get("name", ""),
                    "major": metadata.get("major", ""),
                    "graduation_year": metadata.get("graduation_year", 0),
                    "company_tier": metadata.get("company_tier", ""),
                    "salary_range": metadata.get("salary_range", ""),
                    "placement_status": metadata.get("placement_status", ""),
                    "outcome_score": float(metadata.get("outcome_score", 0.0))
                }
            )
            
            # Upsert point (insert or update)
            self.client.upsert(
                collection_name="alumni",
                points=[point]
            )
            
            logger.info(f"Stored vector for alumni {alumni_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error storing alumni vector: {e}")
            return False
    
    def update_student_vector(
        self,
        student_id: int,
        vector: np.ndarray
    ) -> bool:
        """
        Update existing student vector in Qdrant.
        
        Args:
            student_id: Unique student ID
            vector: Updated 15-dimensional numpy array
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("Qdrant unavailable. Cannot update student vector.")
            return False
        
        try:
            # Get existing point to preserve metadata
            existing = self.client.retrieve(
                collection_name="students",
                ids=[student_id]
            )
            
            if not existing:
                logger.warning(f"Student {student_id} not found in Qdrant")
                return False
            
            # Update vector while preserving metadata
            vector_list = vector.tolist() if isinstance(vector, np.ndarray) else vector
            
            point = PointStruct(
                id=student_id,
                vector=vector_list,
                payload={
                    **existing[0].payload,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            self.client.upsert(
                collection_name="students",
                points=[point]
            )
            
            logger.info(f"Updated vector for student {student_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating student vector: {e}")
            return False
    
    def find_similar_alumni(
        self,
        student_vector: np.ndarray,
        major: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find top K most similar alumni using cosine similarity.
        
        Args:
            student_vector: 15-dimensional student vector
            major: Optional major filter (e.g., "Computer Science")
            top_k: Number of results to return (default: 5)
        
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
        """
        if not self.is_available:
            logger.warning("Qdrant unavailable. Returning empty results.")
            return []
        
        try:
            # Convert numpy array to list
            vector_list = student_vector.tolist() if isinstance(student_vector, np.ndarray) else student_vector
            
            # Build filter for major if specified
            query_filter = None
            if major:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="major",
                            match=MatchValue(value=major)
                        )
                    ]
                )
            
            # Search for similar alumni
            search_result = self.client.query_points(
                collection_name="alumni",
                query=vector_list,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True
            ).points
            
            # Format results
            results = []
            for hit in search_result:
                results.append({
                    "alumni_id": hit.payload.get("alumni_id"),
                    "similarity_score": hit.score,  # Cosine similarity (0-1)
                    "name": hit.payload.get("name", ""),
                    "major": hit.payload.get("major", ""),
                    "graduation_year": hit.payload.get("graduation_year", 0),
                    "company_tier": hit.payload.get("company_tier", ""),
                    "salary_range": hit.payload.get("salary_range", ""),
                    "placement_status": hit.payload.get("placement_status", ""),
                    "outcome_score": hit.payload.get("outcome_score", 0.0)
                })
            
            logger.info(f"Found {len(results)} similar alumni")
            return results
        
        except Exception as e:
            logger.error(f"Error finding similar alumni: {e}")
            return []
    
    def delete_student_vector(self, student_id: int) -> bool:
        """
        Delete student vector from Qdrant.
        
        Args:
            student_id: Unique student ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            self.client.delete(
                collection_name="students",
                points_selector=models.PointIdsList(
                    points=[student_id]
                )
            )
            logger.info(f"Deleted vector for student {student_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting student vector: {e}")
            return False
    
    def delete_alumni_vector(self, alumni_id: int) -> bool:
        """
        Delete alumni vector from Qdrant.
        
        Args:
            alumni_id: Unique alumni ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            self.client.delete(
                collection_name="alumni",
                points_selector=models.PointIdsList(
                    points=[alumni_id]
                )
            )
            logger.info(f"Deleted vector for alumni {alumni_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting alumni vector: {e}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict]:
        """
        Get information about a collection.
        
        Args:
            collection_name: Name of collection (students or alumni)
        
        Returns:
            Dict with collection info or None if unavailable
        """
        if not self.is_available:
            return None
        
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None


# ============================================================================
# POSTGRESQL FALLBACK (when Qdrant unavailable)
# ============================================================================

def cosine_similarity_numpy(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors using NumPy.
    
    Used as fallback when Qdrant is unavailable.
    
    Formula: (A · B) / (||A|| × ||B||)
    
    Args:
        vec_a: First vector
        vec_b: Second vector
    
    Returns:
        Similarity score in [0, 1] range (higher = more similar)
    """
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    similarity = dot_product / (norm_a * norm_b)
    
    # Cosine similarity is in [-1, 1], normalize to [0, 1]
    normalized = (similarity + 1) / 2
    
    return float(normalized)


def find_similar_alumni_fallback(
    student_vector: np.ndarray,
    alumni_vectors: List[Tuple[int, np.ndarray, Dict]],
    major: Optional[str] = None,
    top_k: int = 5
) -> List[Dict]:
    """
    Fallback similarity search using PostgreSQL + NumPy.
    
    Used when Qdrant is unavailable.
    
    Args:
        student_vector: 15-dimensional student vector
        alumni_vectors: List of (alumni_id, vector, metadata) tuples
        major: Optional major filter
        top_k: Number of results to return
    
    Returns:
        List of similar alumni (same format as Qdrant search)
    """
    similarities = []
    
    for alumni_id, alumni_vector, metadata in alumni_vectors:
        # Filter by major if specified
        if major and metadata.get("major") != major:
            continue
        
        # Calculate cosine similarity
        similarity = cosine_similarity_numpy(student_vector, alumni_vector)
        
        similarities.append({
            "alumni_id": alumni_id,
            "similarity_score": similarity,
            "name": metadata.get("name", ""),
            "major": metadata.get("major", ""),
            "graduation_year": metadata.get("graduation_year", 0),
            "company_tier": metadata.get("company_tier", ""),
            "salary_range": metadata.get("salary_range", ""),
            "placement_status": metadata.get("placement_status", ""),
            "outcome_score": metadata.get("outcome_score", 0.0)
        })
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    # Return top K
    return similarities[:top_k]
