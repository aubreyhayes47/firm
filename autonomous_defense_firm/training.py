"""
Module for user-driven training, feedback collection, and model management for the autonomous law firm system.
Practice-area-neutral and extensible for any law firm workflow.
"""
import os
import pickle
from typing import Any, Dict, List

class TrainingManager:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.models = {}  # model_type -> model object
        self.training_data = []  # List of (data_type, data, label)
        self.model_versions = {}  # model_type -> list of version info

    def collect_training_example(self, data_type: str, data: dict, label: Any):
        self.training_data.append({
            'data_type': data_type,
            'data': data,
            'label': label
        })
        # Optionally, store in KB feedback
        self.kb.create_feedback({'data_type': data_type, 'data': data, 'label': label, 'source': 'training'})

    def export_training_data(self, filename: str):
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.training_data, f, indent=2)

    def import_training_data(self, filename: str):
        import json
        with open(filename, 'r', encoding='utf-8') as f:
            self.training_data = json.load(f)

    def train_model(self, model_type: str, params: dict = None):
        # Placeholder: In a real system, this would call out to ML code or a service
        # Here, we just record a dummy model and version
        model = {'type': model_type, 'params': params, 'trained_on': len(self.training_data)}
        self.models[model_type] = model
        self.model_versions.setdefault(model_type, []).append({'model': model, 'version': len(self.model_versions.get(model_type, []))+1})
        return model

    def save_model(self, model_type: str, path: str):
        model = self.models.get(model_type)
        if model:
            with open(path, 'wb') as f:
                pickle.dump(model, f)
            return True
        return False

    def load_model(self, model_type: str, path: str):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.models[model_type] = pickle.load(f)
            return self.models[model_type]
        return None

    def evaluate_model(self, model_type: str, test_data: List[dict]):
        # Placeholder: In a real system, this would run evaluation logic
        model = self.models.get(model_type)
        if not model:
            return None
        return {'model_type': model_type, 'accuracy': 1.0, 'tested_on': len(test_data)}

    def list_models(self):
        return list(self.models.keys())

    def list_model_versions(self, model_type: str):
        return self.model_versions.get(model_type, [])
