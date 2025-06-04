"""
Module for managing LLMs (local and API endpoints) for the autonomous law firm system.
"""
import os
from typing import List, Dict

class LLMManager:
    def __init__(self, config_path='llms.json'):
        self.config_path = config_path
        self.llms = []  # List of dicts: {name, type, path_or_url, is_default}
        self.load()

    def load(self):
        import json
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.llms = json.load(f)
        else:
            self.llms = []

    def save(self):
        import json
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.llms, f, indent=2)

    def list_llms(self) -> List[Dict]:
        return self.llms

    def add_llm(self, name, llm_type, path_or_url, is_default=False):
        if is_default:
            for llm in self.llms:
                llm['is_default'] = False
        self.llms.append({
            'name': name,
            'type': llm_type,  # 'local' or 'api'
            'path_or_url': path_or_url,
            'is_default': is_default
        })
        self.save()

    def remove_llm(self, name):
        self.llms = [llm for llm in self.llms if llm['name'] != name]
        self.save()

    def set_default(self, name):
        found = False
        for llm in self.llms:
            llm['is_default'] = (llm['name'] == name)
            if llm['is_default']:
                found = True
        self.save()
        return found

    def get_default(self):
        for llm in self.llms:
            if llm.get('is_default'):
                return llm
        return None

    def test_llm(self, name):
        # Placeholder: In real use, try to connect or run a test prompt
        llm = next((l for l in self.llms if l['name'] == name), None)
        if not llm:
            return False, 'Not found'
        if llm['type'] == 'api':
            # Try a test API call (not implemented)
            return True, 'API endpoint test not implemented'
        elif llm['type'] == 'local':
            # Check if file/path exists
            return os.path.exists(llm['path_or_url']), 'Local model path check'
        return False, 'Unknown type'
