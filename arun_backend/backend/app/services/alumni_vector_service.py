"""
Alumni Vector Generation Service

This service handles vector generation for imported alumni records.
It integrates with:
- Vector generation service (generate_alumni_vector)
- Qdrant service (store_alumni_vector)
- PostgreSQL (update vector_id reference)

Key responsibilities:
1. Generate 15-dimensional vectors from alumni profiles
2. Calculate outcome scores from placement data
3. Store vectors in Qdrant with metadata
4. Update PostgreSQL with vector references
5. Handle batch processing for CSV imports
"""

import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import numpy as np

from app.models import Alumni, CompanyTierEnum, PlacementStatusEnum
from app.services.vector_generation import generate_alumni_vector
from app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class AlumniVectorService:
    """
    Service for generating and storing alumni vectors.
    
    This service is called after alumni data is imported to:
    1. Generate vectors from alumni profiles
    2. Calculate outcome scores
    3. Store in Qdrant
    4. Update PostgreSQL references
    """
    
    def __init__(self, qdrant_service: Optional[QdrantService] = None):
        """
        Initialize alumni vector service.
        
        Args:
            qdrant_service: Optional Qdrant service instance (creates new if None)
        """
        self.qdrant = qdrant_service or QdrantService()
        
        # Ensure collections exist
        if self.qdrant.is_available:
            self.qdrant.create_collections()
        
        logger.info("Alumni vector service initialized")
    
    def calculate_outcome_score(
        self,
        placement_status: PlacementStatusEnum,
        company_tier: Optional[CompanyTierEnum] = None
    ) -> float:
        """
        Calculate outcome score from placement data.
        
        Outcome scores represent employment quality:
        - Tier1 (FAANG/Top): 90-100
        - Tier2 (Mid-size/Product): 65-80
        - Tier3 (Service/Startup): 50-65
        - Not Placed: 20
        
        Args:
            placement_status: Placed or Not Placed
            company_tier: Tier1, Tier2, Tier3 (if placed)
        
        Returns:
            Outcome score (0-100)
        
        Examples:
            >>> calculate_outcome_score(PlacementStatusEnum.PLACED, CompanyTierEnum.TIER1)
            95.0
            >>> calculate_outcome_score(PlacementStatusEnum.NOT_PLACED, None)
            20.0
        """
        if placement_status == PlacementStatusEnum.NOT_PLACED:
            return 20.0
        
        # Placed - determine score based on company tier
        if company_tier == CompanyTierEnum.TIER1:
            # FAANG/Top companies: 90-100
            return 95.0
        elif company_tier == CompanyTierEnum.TIER2:
            # Mid-size/Product companies: 65-80
            return 72.5
        elif company_tier == CompanyTierEnum.TIER3:
            # Service/Startup companies: 50-65
            return 57.5
        else:
            # Placed but tier unknown - assume Tier2
            return 70.0
    
    def generate_vector_for_alumni(
        self,
        alumni: Alumni,
        db: Session
    ) -> Optional[np.ndarray]:
        """
        Generate vector for a single alumni record.
        
        Args:
            alumni: Alumni database model instance
            db: Database session
        
        Returns:
            15-dimensional numpy array or None if generation fails
        """
        try:
            # Build profile dict for vector generation
            profile = {
                'gpa': float(alumni.gpa) if alumni.gpa else 5.0,
                'attendance': float(alumni.attendance) if alumni.attendance else 75.0,
                'study_hours_per_week': float(alumni.study_hours_per_week) if alumni.study_hours_per_week else 15.0,
                'project_count': alumni.project_count if alumni.project_count else 0
            }
            
            # TODO: In future, fetch alumni skills from skills table
            # For MVP, alumni don't have detailed skill data
            skills = None
            
            # Generate vector using vector generation service
            vector = generate_alumni_vector(profile, skills=skills)
            
            logger.info(f"Generated vector for alumni {alumni.id} ({alumni.name})")
            return vector
        
        except Exception as e:
            logger.error(f"Error generating vector for alumni {alumni.id}: {e}")
            return None
    
    def store_alumni_vector_in_qdrant(
        self,
        alumni: Alumni,
        vector: np.ndarray,
        outcome_score: float
    ) -> bool:
        """
        Store alumni vector in Qdrant with metadata.
        
        Args:
            alumni: Alumni database model instance
            vector: 15-dimensional numpy array
            outcome_score: Calculated outcome score (0-100)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Build metadata for Qdrant
            metadata = {
                'name': alumni.name,
                'major': alumni.major,
                'graduation_year': alumni.graduation_year,
                'company_tier': alumni.company_tier.value if alumni.company_tier else '',
                'salary_range': alumni.salary_range or '',
                'placement_status': alumni.placement_status.value,
                'outcome_score': outcome_score
            }
            
            # Store in Qdrant
            success = self.qdrant.store_alumni_vector(
                alumni_id=alumni.id,
                vector=vector,
                metadata=metadata
            )
            
            if success:
                logger.info(f"Stored vector in Qdrant for alumni {alumni.id}")
            else:
                logger.warning(f"Failed to store vector in Qdrant for alumni {alumni.id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Error storing alumni vector in Qdrant: {e}")
            return False
    
    def update_alumni_vector_reference(
        self,
        alumni: Alumni,
        db: Session
    ) -> bool:
        """
        Update alumni record in PostgreSQL with vector reference.
        
        Args:
            alumni: Alumni database model instance
            db: Database session
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Store vector ID reference (same as alumni ID)
            alumni.vector_id = f"alumni_{alumni.id}"
            db.commit()
            
            logger.info(f"Updated vector reference for alumni {alumni.id}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating alumni vector reference: {e}")
            db.rollback()
            return False
    
    def process_alumni_record(
        self,
        alumni: Alumni,
        db: Session
    ) -> Dict:
        """
        Complete vector generation pipeline for a single alumni.
        
        This method:
        1. Calculates outcome score
        2. Generates vector
        3. Stores in Qdrant
        4. Updates PostgreSQL reference
        
        Args:
            alumni: Alumni database model instance
            db: Database session
        
        Returns:
            dict: Result with keys:
                - success (bool)
                - alumni_id (int)
                - alumni_name (str)
                - outcome_score (float)
                - vector_stored (bool)
                - error (str, optional)
        """
        result = {
            'success': False,
            'alumni_id': alumni.id,
            'alumni_name': alumni.name,
            'outcome_score': 0.0,
            'vector_stored': False
        }
        
        try:
            # Step 1: Calculate outcome score
            outcome_score = self.calculate_outcome_score(
                alumni.placement_status,
                alumni.company_tier
            )
            result['outcome_score'] = outcome_score
            
            logger.info(f"Alumni {alumni.id} ({alumni.name}): "
                       f"Outcome score = {outcome_score}")
            
            # Step 2: Generate vector
            vector = self.generate_vector_for_alumni(alumni, db)
            
            if vector is None:
                result['error'] = "Vector generation failed"
                return result
            
            # Step 3: Store in Qdrant
            vector_stored = self.store_alumni_vector_in_qdrant(
                alumni,
                vector,
                outcome_score
            )
            result['vector_stored'] = vector_stored
            
            if not vector_stored:
                logger.warning(f"Qdrant storage failed for alumni {alumni.id}, "
                             "but continuing (fallback available)")
            
            # Step 4: Update PostgreSQL reference
            reference_updated = self.update_alumni_vector_reference(alumni, db)
            
            if not reference_updated:
                result['error'] = "Failed to update PostgreSQL reference"
                return result
            
            # Success!
            result['success'] = True
            logger.info(f"Successfully processed alumni {alumni.id} ({alumni.name})")
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing alumni {alumni.id}: {e}")
            result['error'] = str(e)
            return result
    
    def process_alumni_batch(
        self,
        alumni_list: List[Alumni],
        db: Session
    ) -> Dict:
        """
        Process multiple alumni records in batch.
        
        This is used after CSV import to generate vectors for all imported alumni.
        
        Args:
            alumni_list: List of Alumni database model instances
            db: Database session
        
        Returns:
            dict: Summary with keys:
                - total (int): Total alumni processed
                - successful (int): Successfully processed
                - failed (int): Failed to process
                - qdrant_stored (int): Stored in Qdrant
                - results (list): Individual results for each alumni
        """
        summary = {
            'total': len(alumni_list),
            'successful': 0,
            'failed': 0,
            'qdrant_stored': 0,
            'results': []
        }
        
        logger.info(f"Processing batch of {len(alumni_list)} alumni records")
        
        for alumni in alumni_list:
            result = self.process_alumni_record(alumni, db)
            summary['results'].append(result)
            
            if result['success']:
                summary['successful'] += 1
            else:
                summary['failed'] += 1
            
            if result['vector_stored']:
                summary['qdrant_stored'] += 1
        
        logger.info(f"Batch processing complete: "
                   f"{summary['successful']}/{summary['total']} successful, "
                   f"{summary['qdrant_stored']} stored in Qdrant")
        
        return summary


# ============================================================================
# GLOBAL SERVICE INSTANCE (Singleton Pattern)
# ============================================================================

_alumni_vector_service: Optional[AlumniVectorService] = None


def get_alumni_vector_service() -> AlumniVectorService:
    """
    Get or create the global alumni vector service instance.
    
    Returns:
        AlumniVectorService: The global service instance
    """
    global _alumni_vector_service
    
    if _alumni_vector_service is None:
        _alumni_vector_service = AlumniVectorService()
        logger.info("Created global alumni vector service instance")
    
    return _alumni_vector_service
