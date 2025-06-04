import unittest
import os
from autonomous_defense_firm.knowledge_base import KnowledgeBase
from autonomous_defense_firm.training import TrainingManager

class TestCLIAndTraining(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()
        self.tm = TrainingManager(self.kb)
        self.backup_file = 'test_backup.json'
        self.training_file = 'test_training.json'

    def tearDown(self):
        if os.path.exists(self.backup_file):
            os.remove(self.backup_file)
        if os.path.exists(self.training_file):
            os.remove(self.training_file)

    def test_backup_and_restore(self):
        self.kb.create_client({'name': 'Alice', 'contact': 'alice@example.com'})
        self.kb.save_to_file(self.backup_file)
        self.kb.clients = []
        self.assertEqual(len(self.kb.clients), 0)
        self.kb.load_from_file(self.backup_file)
        self.assertEqual(len(self.kb.clients), 1)
        self.assertEqual(self.kb.clients[0]['name'], 'Alice')

    def test_feedback_and_training_data(self):
        self.tm.collect_training_example('client', {'name': 'Bob', 'contact': 'bob@example.com'}, 'correct')
        self.assertEqual(len(self.tm.training_data), 1)
        self.tm.export_training_data(self.training_file)
        self.tm.training_data = []
        self.tm.import_training_data(self.training_file)
        self.assertEqual(len(self.tm.training_data), 1)
        self.assertEqual(self.tm.training_data[0]['data']['name'], 'Bob')

    def test_train_and_evaluate_model(self):
        self.tm.collect_training_example('case', {'case_number': '123', 'title': 'Test', 'text': 'abc'}, 'relevant')
        model = self.tm.train_model('dummy_model')
        self.assertIn('type', model)
        self.assertIn('dummy_model', self.tm.models)
        result = self.tm.evaluate_model('dummy_model', [{'case_number': '123', 'title': 'Test', 'text': 'abc'}])
        self.assertIsInstance(result, dict)
        self.assertEqual(result['model_type'], 'dummy_model')

    def test_list_models_and_versions(self):
        self.tm.train_model('dummy_model')
        self.tm.train_model('dummy_model')
        self.assertIn('dummy_model', self.tm.list_models())
        versions = self.tm.list_model_versions('dummy_model')
        self.assertTrue(len(versions) >= 2)

    def test_llm_crud_and_persistence(self):
        # LLM CRUD and persistence test
        local_llm = {
            'name': 'LocalModel',
            'type': 'local',
            'model_path': '/models/local-model.bin'
        }
        created = self.kb.create_llm(local_llm)
        self.assertEqual(created['name'], 'LocalModel')
        self.assertEqual(len(self.kb.list_llms()), 1)
        api_llm = {
            'name': 'APImodel',
            'type': 'api',
            'api_url': 'https://api.llm.com',
            'api_key': 'secret'
        }
        created_api = self.kb.create_llm(api_llm)
        self.assertEqual(created_api['type'], 'api')
        self.assertEqual(len(self.kb.list_llms()), 2)
        self.kb.update_llm(created['id'], {'model_path': '/models/updated.bin'})
        self.assertEqual(self.kb.list_llms()[0]['model_path'], '/models/updated.bin')
        self.kb.set_default_llm(created_api['id'])
        self.assertTrue(self.kb.get_default_llm()['id'] == created_api['id'])
        self.kb.delete_llm(created['id'])
        self.assertEqual(len(self.kb.list_llms()), 1)
        self.kb.save_to_file(self.backup_file)
        self.kb.llms = []
        self.kb.load_from_file(self.backup_file)
        self.assertEqual(len(self.kb.list_llms()), 1)
        self.assertEqual(self.kb.list_llms()[0]['name'], 'APImodel')

    def test_profile_crud_and_persistence(self):
        # Profile CRUD and persistence test
        if not hasattr(self.kb, 'profiles'):
            self.kb.profiles = []
            self.kb.active_profile_id = None
        profile = {
            'id': 'test-profile-id',
            'name': 'Criminal Defense',
            'jurisdiction': 'Tennessee',
            'practice_area': 'Criminal',
            'prompt_template': 'You are a criminal defense expert.'
        }
        self.kb.profiles.append(profile)
        self.kb.active_profile_id = 'test-profile-id'
        self.kb.save_to_file(self.backup_file)
        self.kb.profiles = []
        self.kb.active_profile_id = None
        self.kb.load_from_file(self.backup_file)
        self.assertEqual(len(self.kb.profiles), 1)
        self.assertEqual(self.kb.profiles[0]['name'], 'Criminal Defense')
        self.assertEqual(self.kb.active_profile_id, 'test-profile-id')

if __name__ == "__main__":
    unittest.main()
