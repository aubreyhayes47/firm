"""
Module for defining the AI's purpose, curriculum, and target skills.
Practice-area-neutral version.
"""

class LegalEducationConfig:
    def __init__(self, jurisdiction=None, areas_of_law=None, skills=None, user_role=None):
        self.jurisdiction = jurisdiction or ["Any jurisdiction"]
        self.areas_of_law = areas_of_law or ["All practice areas"]
        self.skills = skills or [
            "Legal Research",
            "Drafting",
            "Analysis",
            "Client Communication",
            "Case Management"
        ]
        self.user_role = user_role or "Attorney or Legal Professional"

    def to_dict(self):
        return {
            "jurisdiction": self.jurisdiction,
            "areas_of_law": self.areas_of_law,
            "skills": self.skills,
            "user_role": self.user_role
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            jurisdiction=d.get("jurisdiction", []),
            areas_of_law=d.get("areas_of_law", []),
            skills=d.get("skills", []),
            user_role=d.get("user_role", "")
        )

# Practice-area-neutral default config
DEFAULT_CONFIG = LegalEducationConfig()
