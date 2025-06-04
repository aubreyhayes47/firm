import unittest
from autonomous_defense_firm.nlp_engine import NLPEngine

class TestNLPEngine(unittest.TestCase):
    def setUp(self):
        self.engine = NLPEngine()

    def test_legal_tokenize(self):
        tokens = self.engine.legal_tokenize("Tennessee v. Smith, 2020")
        self.assertIn("Tennessee", tokens)

    def test_named_entity_recognition(self):
        entities = self.engine.named_entity_recognition("Judge John Doe presided.")
        self.assertIsInstance(entities, list)

    def test_parse_sentence(self):
        parsed = self.engine.parse_sentence("The defendant was found guilty.")
        self.assertIsInstance(parsed, dict)

    def test_intent_recognition(self):
        intent = self.engine.intent_recognition("What is the statute of limitations?")
        self.assertIsInstance(intent, str)

    def test_query_expansion(self):
        expanded = self.engine.query_expansion("assault")
        self.assertIsInstance(expanded, list)
        self.assertIn("assault", expanded)

    def test_generate_answer(self):
        answer = self.engine.generate_answer("context", "What is the law?")
        self.assertIsInstance(answer, str)

if __name__ == "__main__":
    unittest.main()
