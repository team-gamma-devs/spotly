from pydantic import BaseModel, Field
from typing import List, Literal


class CVInfoSchema(BaseModel):
    """Schema for extracting structured information from a CV/Resume"""

    first_name: str = Field(
        description="First name of the candidate. If there are multiple names, use only the first one."
    )
    last_name: str = Field(
        description="Last name(s) of the candidate. If there are multiple last names, use only the first one."
    )
    skills: List[str] = Field(
        description="""Complete list of technical and professional skills mentioned in the CV.
        Include: programming languages, frameworks, tools, databases, methodologies.
        Don't include protocols or conventional frameworks like "JWT" (Not too big to be considerated).
        Examples: ["Python", "FastAPI", "PostgreSQL", "Docker", "Scrum", "Git"]
        Resume decorators as "RESTfull" in only "REST" or "AWS Cognito" (And AWS techs) in "AWS"
        Extract ONLY explicitly mentioned skills in CV/Resumee. Do not infer or assume skills.
        Separate each technology individually (e.g., "Python/Django" should be ["Python", "Django"])."""
    )
    english_level: Literal[
        "basic",
        "intermediate",
        "advanced",
    ] = Field(
        description="""English proficiency level of the candidate as stated in the CV.
        Classify according to these options:
        - "basic": A1-A2, beginner, elementary
        - "intermediate": B1-B2, conversational, intermediate
        - "advanced": C1-C2, fluent, professional, business level
        - "basic": If English level is not mentioned in the CV.
        
        If certifications are mentioned (TOEFL, IELTS, Cambridge), use those to classify the level."""
    )
    linkedin_url: str = Field(
        description="""Extract only the public LinkedIn URL from this CV. Strict rules:

        - The URL always ends right before "(LinkedIn)".
        - Include absolutely everything between "/in/" or "/pub/" and "(LinkedIn)", including hyphens, numbers, letters, and underscores.
        - Add "https://" prefix if missing.
        - Do not invent, modify, or truncate the URL in any way.
        - Return only the LinkedIn URL.
        - Example: if the CV contains "www.linkedin.com/in/john-doe-7451b2597 (LinkedIn)", return "https://www.linkedin.com/in/john-doe-7451b2597".
        """
    )
    works_in_it: bool = Field(
        description="""Does the candidate currently work or have recent experience in IT/Technology?
        Extract ONLY explicitly mentioned works in CV/Resumee. Do not infer or assume works.
        IGNORE technical skills sections, and ALL education/training.
        Return True if:
        - ONLY if the person's CURRENT or most recent job 
        (the one they are working in NOW or worked most recently) is:
        - A technical role such as: Developer, Programmer, Software Engineer, 
        DevOps Engineer, QA Engineer, Data Engineer, System Administrator, Technical Lead, etc.
        - At a technology company OR in a technical department
        
        Return False if:
        - Only has academic education without professional work experience.
        - Don't include as work personal projects or recentl projects.
        - Does not work in IT or works in computer repair actually.
        - Is not currently working.
        - Is a freelance or ocasional work in IT.
        - Is a student without professional IT experience
        - Only has personal projects or hobby coding"""
    )
