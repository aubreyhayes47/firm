import unittest
from autonomous_defense_firm.legal_education import DEFAULT_CONFIG

class TestLegalEducation(unittest.TestCase):
    def test_default_config(self):
        self.assertIn("Tennessee State criminal law", DEFAULT_CONFIG.jurisdiction)
        self.assertIn("Criminal Law", DEFAULT_CONFIG.areas_of_law)
        self.assertIn("Finding Facts", DEFAULT_CONFIG.skills)
        self.assertEqual(DEFAULT_CONFIG.user_role, "Tennessee attorney (owner/supervising)")

if __name__ == "__main__":
    unittest.main()
