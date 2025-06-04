import unittest
from autonomous_defense_firm.retrieval import RetrievalEngine

class TestRetrievalEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RetrievalEngine()

    def test_create_index(self):
        self.engine.create_index(["doc1", "doc2"])
        # No assertion, just ensure no error

    def test_vector_search(self):
        results = self.engine.vector_search("search query")
        self.assertIsInstance(results, list)

    def test_rank_results(self):
        ranked = self.engine.rank_results(["a", "b"])
        self.assertEqual(ranked, ["a", "b"])

if __name__ == "__main__":
    unittest.main()
