import unittest
from autonomous_defense_firm.legal_education import DEFAULT_CONFIG, LegalEducationConfig

class TestLegalEducation(unittest.TestCase):
    def test_default_config(self):
        self.assertIn("Tennessee State criminal law", DEFAULT_CONFIG.jurisdiction)
        self.assertIn("Criminal Law", DEFAULT_CONFIG.areas_of_law)
        self.assertIn("Finding Facts", DEFAULT_CONFIG.skills)
        self.assertEqual(DEFAULT_CONFIG.user_role, "Tennessee attorney (owner/supervising)")

    def test_custom_config(self):
        config = LegalEducationConfig(
            jurisdiction=["Federal"],
            areas_of_law=["Civil Rights"],
            skills=["Drafting Help"],
            user_role="Paralegal"
        )
        self.assertEqual(config.jurisdiction, ["Federal"])
        self.assertEqual(config.areas_of_law, ["Civil Rights"])
        self.assertEqual(config.skills, ["Drafting Help"])
        self.assertEqual(config.user_role, "Paralegal")

if __name__ == "__main__":
    unittest.main()
