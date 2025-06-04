import unittest
from autonomous_defense_firm.knowledge_base import KnowledgeBase
from unittest.mock import patch

class TestKnowledgeBase(unittest.TestCase):
    def test_add_and_ingest(self):
        kb = KnowledgeBase()
        kb.add_source('primary', 'Tennessee Code Annotated')
        kb.ingest_document({'title': 'Test Statute', 'text': 'Some law text.'})
        self.assertIn('Tennessee Code Annotated', kb.primary_sources)
        self.assertEqual(len(kb.documents), 1)

    @patch('autonomous_defense_firm.knowledge_base.requests.get')
    def test_fetch_caselaw_access_project(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": [{"caseName": "Test v. Test"}], "next": None}
        kb = KnowledgeBase()
        results = kb.fetch_caselaw_access_project(max_pages=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["caseName"], "Test v. Test")

    @patch('autonomous_defense_firm.knowledge_base.requests.get')
    def test_fetch_courtlistener(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": [{"case_name": "Test v. Test"}], "next": None}
        kb = KnowledgeBase()
        results = kb.fetch_courtlistener(max_pages=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["case_name"], "Test v. Test")

    def test_human_review(self):
        kb = KnowledgeBase()
        # Simulate human approval for all
        with patch('builtins.input', return_value='y'):
            docs = [{"caseName": "Test v. Test"}, {"caseName": "Test2 v. Test2"}]
            approved = kb.human_review(docs)
            self.assertEqual(len(approved), 2)

    def test_llm_crud_and_persistence(self):
        kb = KnowledgeBase()
        # Create local LLM
        local_llm = {
            'name': 'LocalModel',
            'type': 'local',
            'model_path': '/models/local-model.bin'
        }
        created = kb.create_llm(local_llm)
        self.assertEqual(created['name'], 'LocalModel')
        self.assertEqual(len(kb.list_llms()), 1)
        # Create API LLM
        api_llm = {
            'name': 'APImodel',
            'type': 'api',
            'api_url': 'https://api.llm.com',
            'api_key': 'secret'
        }
        created_api = kb.create_llm(api_llm)
        self.assertEqual(created_api['type'], 'api')
        self.assertEqual(len(kb.list_llms()), 2)
        # Update LLM
        kb.update_llm(created['id'], {'model_path': '/models/updated.bin'})
        self.assertEqual(kb.list_llms()[0]['model_path'], '/models/updated.bin')
        # Set default LLM
        kb.set_default_llm(created_api['id'])
        self.assertTrue(kb.get_default_llm()['id'] == created_api['id'])
        # Delete LLM
        kb.delete_llm(created['id'])
        self.assertEqual(len(kb.list_llms()), 1)
        # Test persistence
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            kb.save_to_file(tf.name)
            kb2 = KnowledgeBase()
            kb2.load_from_file(tf.name)
            self.assertEqual(len(kb2.list_llms()), 1)
            self.assertEqual(kb2.list_llms()[0]['name'], 'APImodel')
        os.remove(tf.name)

    def test_crud_and_persistence_all_types(self):
        kb = KnowledgeBase()
        # Test data for all types
        test_data = [
            ('client', {'name': 'Alice', 'contact': 'alice@example.com'}, kb.create_client, kb.list_clients, kb.update_client, kb.delete_client),
            ('case_file', {'title': 'Case A', 'client_id': 'cid'}, kb.create_case_file, kb.list_case_files, kb.update_case_file, kb.delete_case_file),
            ('legal_research', {'topic': 'Miranda', 'content': 'Miranda rights summary'}, kb.create_legal_research, kb.list_legal_research, kb.update_legal_research, kb.delete_legal_research),
            ('contract', {'parties': 'A,B', 'effective_date': '2025-01-01'}, kb.create_contract, kb.list_contracts, kb.update_contract, kb.delete_contract),
            ('internal_doc', {'title': 'Policy', 'content': 'Policy text'}, kb.create_internal_doc, kb.list_internal_docs, kb.update_internal_doc, kb.delete_internal_doc),
            ('calendar_event', {'title': 'Hearing', 'datetime': '2025-06-04T10:00', 'participants': 'Alice,Bob'}, kb.create_calendar_event, kb.list_calendar_events, kb.update_calendar_event, kb.delete_calendar_event),
            ('note', {'author': 'Alice', 'body': 'Note body'}, kb.create_note, kb.list_notes, kb.update_note, kb.delete_note),
            ('feedback', {'data_type': 'case', 'data': 'test', 'label': 'correct'}, kb.create_feedback, kb.list_feedback, kb.update_feedback, kb.delete_feedback),
            ('ethics_record', {'issue': 'Conflict', 'date': '2025-06-04', 'resolution': 'Resolved'}, kb.create_ethics_record, kb.list_ethics_records, kb.update_ethics_record, kb.delete_ethics_record),
            ('financial_record', {'amount': 100, 'date': '2025-06-04', 'description': 'Fee'}, kb.create_financial_record, kb.list_financial_records, kb.update_financial_record, kb.delete_financial_record),
            ('communication_log', {'participants': 'Alice,Bob', 'timestamp': '2025-06-04T10:00', 'content': 'Call'}, kb.create_communication_log, kb.list_communication_logs, kb.update_communication_log, kb.delete_communication_log),
            ('template', {'name': 'Default', 'content': 'Template text'}, kb.create_template, kb.list_templates, kb.update_template, kb.delete_template),
            ('external_data', {'source': 'API', 'content': 'External info'}, kb.create_external_data, kb.list_external_data, kb.update_external_data, kb.delete_external_data),
        ]
        for label, data, create_fn, list_fn, update_fn, delete_fn in test_data:
            # Create
            created = create_fn(data)
            self.assertTrue('id' in created)
            self.assertEqual(len(list_fn()), 1)
            # Update
            update = {k: v for k, v in data.items()}
            for k in update:
                if isinstance(update[k], str):
                    update[k] += '_updated'
            update_fn(created['id'], update)
            updated = list_fn()[0]
            for k in update:
                self.assertTrue(str(update[k]).replace('_updated','') in str(updated[k]))
            # Delete
            delete_fn(created['id'])
            self.assertEqual(len(list_fn()), 0)
        # Test persistence for one type
        kb.create_client({'name': 'Bob', 'contact': 'bob@example.com'})
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            kb.save_to_file(tf.name)
            kb2 = KnowledgeBase()
            kb2.load_from_file(tf.name)
            self.assertEqual(len(kb2.list_clients()), 1)
            self.assertEqual(kb2.list_clients()[0]['name'], 'Bob')
        os.remove(tf.name)

    def test_validation_and_error_handling(self):
        kb = KnowledgeBase()
        # Missing required fields
        with self.assertRaises(ValueError):
            kb.create_client({'contact': 'no name'})
        with self.assertRaises(ValueError):
            kb.create_case_file({'title': 'No client_id'})
        # Update with invalid data
        c = kb.create_client({'name': 'Test', 'contact': 't'})
        with self.assertRaises(ValueError):
            kb.update_client(c['id'], {'name': ''})
        # Delete non-existent
        self.assertFalse(kb.delete_client('nonexistent'))
        # Update non-existent
        self.assertFalse(kb.update_client('nonexistent', {'name': 'X'}))


if __name__ == "__main__":
    unittest.main()
