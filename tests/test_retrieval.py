import unittest
from autonomous_defense_firm.retrieval import RetrievalEngine

class TestRetrievalEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RetrievalEngine()
        self.docs = [
            {"id": 1, "text": "Tennessee criminal law applies."},
            {"id": 2, "text": "Federal law may also apply."}
        ]

    def test_create_index(self):
        # Should not raise error
        self.engine.create_index(self.docs)

    def test_vector_search(self):
        results = self.engine.vector_search("Tennessee")
        self.assertIsInstance(results, list)

    def test_rank_results(self):
        ranked = self.engine.rank_results(self.docs)
        self.assertEqual(ranked, self.docs)

if __name__ == "__main__":
    unittest.main()
