from typing import Optional, List, Dict, Any, Literal


class TutorFeedback:
    def __init__(
        self,
        tutor_id: Optional[str],
        professional_score: Optional[
            Literal["poor", "avergae", "very good", "excellent"]
        ],
        technical_score: Optional[Literal["poor", "avergae", "very good", "excellent"]],
        comments: Optional[List[Dict[str, Any]]],
    ):
        self.tutor_id: Optional[str]
        self.professional_score = professional_score
        self.technical_score = technical_score
        self.comments = comments
