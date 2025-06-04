import unittest
from autonomous_defense_firm.knowledge_base import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):
    def test_add_and_ingest(self):
        kb = KnowledgeBase()
        kb.add_source('primary', 'Tennessee Code Annotated')
        kb.ingest_document({'title': 'Test Statute', 'text': 'Some law text.'})
        self.assertIn('Tennessee Code Annotated', kb.primary_sources)
        self.assertEqual(len(kb.documents), 1)

if __name__ == "__main__":
    unittest.main()
