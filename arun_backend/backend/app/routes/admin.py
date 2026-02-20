"""
Admin routes for Trajectory Engine MVP

This module provides admin-only endpoints for:
- Alumni data import (CSV upload)
- CSV template download
- Analytics and reporting
- System management

All endpoints require admin authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import io
import csv
from datetime import datetime

from app.db import get_db
from app.models import User
from app.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ============================================================================
# DEPENDENCY: Require Admin Role
# ============================================================================

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure user has admin role.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User: The admin user
    
    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============================================================================
# CSV TEMPLATE DOWNLOAD ENDPOINT (Task 19.4)
# ============================================================================

@router.get("/alumni-template")
async def download_alumni_template(
    admin: User = Depends(require_admin)
):
    """
    Download CSV template for alumni data import.
    
    Returns a CSV file with:
    - Header row with all required columns
    - 3 example rows with sample data
    - Comments explaining each field
    
    **Required columns:**
    - name: Alumni full name
    - major: Major/specialization (e.g., "Computer Science")
    - graduation_year: Year of graduation (e.g., 2023)
    - gpa: GPA on 10.0 scale (0.0-10.0)
    - attendance: Attendance percentage (0-100)
    - placement_status: "Placed" or "Not Placed"
    - company_tier: "Tier1", "Tier2", or "Tier3" (if placed)
    - role_title: Job role (e.g., "Software Engineer")
    - salary_range: Salary range (e.g., "15-20 LPA")
    - role_to_major_match_score: How well job matches major (0-100)
    
    **Optional columns:**
    - study_hours_per_week: Average study hours per week
    - project_count: Number of projects completed
    
    Returns:
        StreamingResponse: CSV file download
    """
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    headers = [
        'name',
        'major',
        'graduation_year',
        'gpa',
        'attendance',
        'placement_status',
        'company_tier',
        'role_title',
        'salary_range',
        'role_to_major_match_score',
        'study_hours_per_week',
        'project_count'
    ]
    writer.writerow(headers)
    
    # Write example rows
    example_rows = [
        [
            'Rajesh Kumar',
            'Computer Science',
            '2023',
            '8.5',
            '90',
            'Placed',
            'Tier1',
            'Software Engineer',
            '15-20 LPA',
            '95',
            '25',
            '5'
        ],
        [
            'Priya Sharma',
            'Computer Science',
            '2023',
            '7.8',
            '85',
            'Placed',
            'Tier2',
            'Full Stack Developer',
            '8-12 LPA',
            '85',
            '20',
            '3'
        ],
        [
            'Amit Patel',
            'Mechanical Engineering',
            '2023',
            '7.0',
            '80',
            'Placed',
            'Tier3',
            'Junior Engineer',
            '5-7 LPA',
            '70',
            '18',
            '2'
        ],
        [
            'Sneha Reddy',
            'Business Administration',
            '2023',
            '6.5',
            '70',
            'Not Placed',
            '',
            '',
            '',
            '',
            '15',
            '1'
        ]
    ]
    
    for row in example_rows:
        writer.writerow(row)
    
    # Get CSV content
    csv_content = output.getvalue()
    output.close()
    
    # Create streaming response
    response = StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=alumni_import_template_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )
    
    return response


@router.get("/alumni-template/info")
async def get_template_info(
    admin: User = Depends(require_admin)
):
    """
    Get information about the alumni CSV template format.
    
    Returns detailed field descriptions and validation rules.
    
    Returns:
        dict: Template information with field descriptions
    """
    return {
        "template_name": "Alumni Import Template",
        "version": "1.0",
        "description": "CSV template for importing historical alumni data",
        "required_fields": [
            {
                "name": "name",
                "type": "string",
                "description": "Alumni full name",
                "example": "Rajesh Kumar",
                "validation": "Required, non-empty"
            },
            {
                "name": "major",
                "type": "string",
                "description": "Major/specialization",
                "example": "Computer Science",
                "validation": "Required, will be standardized by LLM"
            },
            {
                "name": "graduation_year",
                "type": "integer",
                "description": "Year of graduation",
                "example": "2023",
                "validation": "Required, 4-digit year"
            },
            {
                "name": "gpa",
                "type": "float",
                "description": "GPA on 10.0 scale",
                "example": "8.5",
                "validation": "Required, 0.0-10.0 (will be normalized if on different scale)"
            },
            {
                "name": "attendance",
                "type": "float",
                "description": "Attendance percentage",
                "example": "90",
                "validation": "Required, 0-100"
            },
            {
                "name": "placement_status",
                "type": "enum",
                "description": "Placement status",
                "example": "Placed",
                "validation": "Required, must be 'Placed' or 'Not Placed'"
            },
            {
                "name": "company_tier",
                "type": "enum",
                "description": "Company tier (if placed)",
                "example": "Tier1",
                "validation": "Required if placed, must be 'Tier1', 'Tier2', or 'Tier3'"
            },
            {
                "name": "role_title",
                "type": "string",
                "description": "Job role title",
                "example": "Software Engineer",
                "validation": "Required if placed"
            },
            {
                "name": "salary_range",
                "type": "string",
                "description": "Salary range",
                "example": "15-20 LPA",
                "validation": "Required if placed"
            },
            {
                "name": "role_to_major_match_score",
                "type": "float",
                "description": "How well job matches major (percentage)",
                "example": "95",
                "validation": "Required if placed, 0-100"
            }
        ],
        "optional_fields": [
            {
                "name": "study_hours_per_week",
                "type": "float",
                "description": "Average study hours per week during college",
                "example": "25",
                "validation": "Optional, 0-40"
            },
            {
                "name": "project_count",
                "type": "integer",
                "description": "Number of projects completed during college",
                "example": "5",
                "validation": "Optional, 0+"
            }
        ],
        "company_tiers": {
            "Tier1": "FAANG/Top companies (Google, Microsoft, Amazon, etc.)",
            "Tier2": "Mid-size/Product companies (Infosys, TCS, Wipro, etc.)",
            "Tier3": "Service/Startup companies"
        },
        "notes": [
            "All text fields will be cleaned and standardized by LLM",
            "GPA will be normalized to 10.0 scale if provided in different format",
            "Major names will be standardized (e.g., 'Comp Sci' → 'Computer Science')",
            "Empty fields for 'Not Placed' alumni are acceptable",
            "Vectors will be automatically generated after import"
        ]
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def admin_health_check(
    admin: User = Depends(require_admin)
):
    """
    Health check endpoint for admin routes.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "admin",
        "timestamp": datetime.utcnow().isoformat(),
        "admin_email": admin.email
    }
