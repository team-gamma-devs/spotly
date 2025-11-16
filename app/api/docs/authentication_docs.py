"""
OpenAPI documentation for authentication endpoints.
"""

LOGIN_DOCS = {
    "summary": "Send magic link login email",
    "description": """
    Initiate the passwordless authentication flow by sending a magic link to the user's email.
    
    **Authentication Flow:**
    1. User submits their email address
    2. System validates the email against existing invitations
    3. A magic link is generated and sent to the email
    4. User clicks the link to complete authentication
    
    **Requirements:**
    - Email must be associated with a valid, non-expired invitation
    - User must have been invited to the platform
    
    **Security:**
    - Magic links are time-limited
    - Each link can only be used once
    - Invitation must not be expired
    """,
    "responses": {
        200: {
            "description": "Magic link sent successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Magic link sent to user@example.com"}
                }
            },
        },
        403: {
            "description": "No invitation found for this email",
            "content": {
                "application/json": {
                    "example": {"detail": "No invitation found for this email address"}
                }
            },
        },
        410: {
            "description": "Invitation has expired",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Your invitation has expired. Please contact an administrator."
                    }
                }
            },
        },
    },
}


AUTH_ME_DOCS = {
    "summary": "Get current user basic information",
    "description": """
    Retrieve basic profile information for the currently authenticated user.
    
    **Returned Data:**
    - User ID
    - First and last name
    - User role (graduate/manager)
    - Avatar URL (if available)
    - First-time login status
    
    **Authentication:**
    - Requires valid JWT token in Authorization header
    - Token must not be expired
    
    **Use Cases:**
    - Display user info in navigation/header
    - Check user role for UI permissions
    - Determine if onboarding flow should be shown
    """,
    "responses": {
        200: {
            "description": "User information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123",
                        "firstName": "John",
                        "lastName": "Doe",
                        "role": "graduate",
                        "avatarUrl": "https://example.com/avatar.jpg",
                        "isFirstTime": False,
                    }
                }
            },
        },
        401: {
            "description": "User not authenticated or token invalid",
            "content": {
                "application/json": {
                    "example": {"detail": "User not logged in or session expired"}
                }
            },
        },
    },
}


AUTH_ME_FULL_DOCS = {
    "summary": "Get current user complete profile",
    "description": """
    Retrieve the complete profile information for the currently authenticated user,
    including CV details, tutor feedback, and all personal information.
    
    **Returned Data:**
    - All basic user information (from `/me`)
    - Email address
    - Cohort number
    - Complete CV information:
      - Personal CV URL
      - LinkedIn profile URL
      - Skills list
      - English proficiency level
      - IT work status
    - Tutor feedback history (if available)
    - Account timestamps (created/updated)
    
    **Authentication:**
    - Requires valid JWT token in Authorization header
    - Token must not be expired
    
    **Use Cases:**
    - Display full user profile page
    - Show CV and feedback information
    - Generate user reports
    - Profile editing forms
    
    **Privacy:**
    - Users can only access their own full profile
    - Managers may have different access levels (implementation dependent)
    """,
    "responses": {
        200: {
            "description": "Complete user profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123",
                        "firstName": "John",
                        "lastName": "Doe",
                        "email": "john@example.com",
                        "avatarUrl": "https://example.com/avatar.jpg",
                        "role": "graduate",
                        "cohort": 5,
                        "cvInfo": {
                            "personalCvUrl": "https://example.com/cv.pdf",
                            "linkedinUrl": "https://linkedin.com/in/johndoe",
                            "skills": ["Python", "React", "AWS"],
                            "englishLevel": "Advanced",
                            "worksInIt": True,
                            "lastUpdate": "2025-01-15T10:30:00Z",
                        },
                        "tutorsFeedback": [
                            {
                                "id": "fb_123",
                                "tutorId": "tutor_456",
                                "tutorName": "Jane Smith",
                                "professionalScore": "Excellent",
                                "technicalScore": "Good",
                                "annotation": "Great progress and communication skills.",
                                "createdAt": "2025-01-10T14:20:00Z",
                            }
                        ],
                        "createdAt": "2024-12-01T09:00:00Z",
                        "updatedAt": "2025-01-15T10:30:00Z",
                    }
                }
            },
        },
        401: {
            "description": "User not authenticated or token invalid",
            "content": {
                "application/json": {
                    "example": {"detail": "User not logged in or session expired"}
                }
            },
        },
    },
}
