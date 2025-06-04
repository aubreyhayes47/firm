"""
Module for defining the AI's purpose, curriculum, and target skills.
"""
# ...existing code...

class LegalEducationConfig:
    def __init__(self, jurisdiction, areas_of_law, skills, user_role):
        self.jurisdiction = jurisdiction
        self.areas_of_law = areas_of_law
        self.skills = skills
        self.user_role = user_role

# Example default config for Tennessee criminal law
DEFAULT_CONFIG = LegalEducationConfig(
    jurisdiction=["Tennessee State criminal law", "Relevant Federal criminal law for TN cases"],
    areas_of_law=["Criminal Law"],
    skills=[
        "Finding Facts",
        "Understanding Laws",
        "Analyzing Cases",
        "Spotting Issues",
        "Drafting Help"
    ],
    user_role="Tennessee attorney (owner/supervising)"
)
