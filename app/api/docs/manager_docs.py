"""
OpenAPI documentation for manager endpoints.
"""

UPLOAD_CSV_DOCS = {
    "summary": "Upload CSV file with graduate invitations",
    "description": """
    Upload a CSV file containing graduate invitation data. The file will be processed
    asynchronously and invitations will be sent in the background.
    
    **CSV Requirements:**
    - File must be in CSV format (.csv extension)
    - Maximum file size: configured by MAX_CSV_SIZE setting
    - Must contain required columns for invitation processing
    
    **Process:**
    1. File is validated for format and size
    2. CSV content is parsed and validated
    3. Invitations are generated
    4. Email invitations are sent asynchronously
    """,
    "responses": {
        202: {
            "description": "CSV accepted and processing started",
            "content": {
                "application/json": {
                    "example": {"message": "Invitations generated successfully"}
                }
            },
        },
        400: {
            "description": "Invalid CSV format or content",
            "content": {
                "application/json": {"example": {"detail": "Invalid CSV structure"}}
            },
        },
        413: {
            "description": "File size exceeds maximum allowed",
            "content": {
                "application/json": {
                    "example": {"detail": "file.csv exceeds 10.0MB limit"}
                }
            },
        },
        422: {
            "description": "Missing required columns in CSV",
            "content": {
                "application/json": {
                    "example": {"detail": "Missing required columns: email, firstName"}
                }
            },
        },
    },
}


GET_FILTERS_DOCS = {
    "summary": "Get available filter options",
    "description": """
    Retrieve all available technology filters that can be used to search and filter graduates.
    
    Returns a list of technology names/tags that graduates have in their profiles.
    These filters can be used in the `/search_graduates` endpoint.
    """,
    "responses": {
        200: {
            "description": "List of available filters retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "filters": ["Python", "JavaScript", "React", "Node.js", "AWS"]
                    }
                }
            },
        }
    },
}


SEARCH_GRADUATES_DOCS = {
    "summary": "Search and filter graduates",
    "description": """
    Search for graduates using various filters including technologies, English level, and tutor feedback.
    
    **Filters:**
    - **technologies**: List of required technology skills
    - **englishLevels**: Minimum English proficiency levels
    - **tutorsFeedback**: Filter by specific tutor feedback IDs
    
    **Pagination:**
    - Results are paginated for better performance
    - Default page size: 20 items
    - Maximum page size: 100 items
    
    Returns a paginated list of graduates matching the specified criteria.
    """,
    "responses": {
        200: {
            "description": "Filtered graduates retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "123",
                                "firstName": "John",
                                "lastName": "Doe",
                                "email": "john@example.com",
                                "englishLevel": "Advanced",
                                "avatarUrl": "https://example.com/avatar.jpg",
                                "cohort": 5,
                                "techStack": ["Python", "React"],
                                "linkedinUrl": "https://linkedin.com/in/johndoe",
                                "worksInIt": True,
                                "createdAt": "2025-01-15T10:30:00Z",
                                "updatedAt": "2025-01-16T14:20:00Z",
                            }
                        ],
                        "pages": 10,
                        "page": 1,
                        "limit": 20,
                    }
                }
            },
        }
    },
}


INCOMPLETE_FEEDBACKS_DOCS = {
    "summary": "Get incomplete feedback list",
    "description": """
    Retrieve a list of graduates who still need feedback from the current tutor/manager.
    
    This endpoint returns graduates who:
    - Are assigned to the current manager
    - Have not yet received feedback
    - Are awaiting evaluation
    
    Useful for managers to track pending feedback tasks.
    """,
    "responses": {
        200: {
            "description": "List of graduates with incomplete feedback",
            "content": {
                "application/json": {
                    "example": {
                        "id": "456",
                        "firstName": "Jane",
                        "lastName": "Smith",
                        "cohort": 5,
                    }
                }
            },
        }
    },
}


CREATE_FEEDBACK_DOCS = {
    "summary": "Create tutor feedback for a graduate",
    "description": """
    Submit feedback for a specific graduate. Feedback can include professional scores,
    technical scores, and written annotations.
    
    **Required Fields:**
    - **graduatedId**: The ID of the graduate receiving feedback
    
    **Optional Fields (at least one required):**
    - **professionalScore**: Professional skills rating (Poor, Average, Good, Excellent)
    - **technicalScore**: Technical skills rating (Poor, Average, Good, Excellent)
    - **annotation**: Written feedback/comments
    
    Note: At least one of the optional fields must be provided.
    """,
    "responses": {
        201: {
            "description": "Feedback created successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Feedback created successfully"}
                }
            },
        },
        400: {
            "description": "Invalid feedback data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "At least one of annotation, technical_score, or professional_score must be provided"
                    }
                }
            },
        },
    },
}


DELETE_FEEDBACK_DOCS = {
    "summary": "Delete tutor feedback",
    "description": """
    Delete a specific feedback entry by its ID.
    
    **Warning:** This action is permanent and cannot be undone.
    
    Only the tutor who created the feedback or a manager can delete it.
    """,
    "responses": {
        204: {"description": "Feedback deleted successfully"},
        400: {
            "description": "Delete operation failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Feedback not found or unauthorized"}
                }
            },
        },
    },
}


FILTER_INVITATIONS_DOCS = {
    "summary": "Search and filter invitations",
    "description": """
    Retrieve a paginated list of graduate invitations with optional search filtering.
    
    **Search:**
    - Filter invitations by name or email using the `searchTerm` parameter
    - Returns all invitations if no search term is provided
    
    **Pagination:**
    - Default page size: 20 items
    - Maximum page size: 100 items
    
    Useful for managing and tracking invitation status.
    """,
    "responses": {
        200: {
            "description": "Invitations retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "inv_123",
                                "fullName": "John Doe",
                                "email": "john@example.com",
                                "cohort": 5,
                                "logState": False,
                                "createdAt": "2025-01-15T10:30:00Z",
                                "expiresAt": "2025-02-15T10:30:00Z",
                            }
                        ],
                        "pages": 5,
                        "page": 1,
                        "limit": 20,
                    }
                }
            },
        }
    },
}


DELETE_INVITATION_DOCS = {
    "summary": "Delete a graduate invitation",
    "description": """
    Delete a specific invitation by its ID.
    
    **Use cases:**
    - Remove duplicate invitations
    - Cancel invitations sent by mistake
    - Clean up expired invitations
    
    **Warning:** This action is permanent and cannot be undone.
    The graduate will not be able to use this invitation link after deletion.
    """,
    "responses": {
        204: {"description": "Invitation deleted successfully"},
        400: {
            "description": "Delete operation failed",
            "content": {
                "application/json": {"example": {"detail": "Invitation not found"}}
            },
        },
    },
}
