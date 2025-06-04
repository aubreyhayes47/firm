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

def run_llm_query(llm, prompt):
    """
    Run a query against the specified LLM (local or API).
    Returns (response, explainability_info).
    Supports OpenAI, Anthropic, HuggingFace, and local models.
    """
    llm_type = llm.get('type')
    name = llm.get('name')
    provider = llm.get('provider', '').lower() if llm.get('provider') else ''
    api_url = llm.get('api_url', '')

    # OpenAI
    if (llm_type == 'api' and ('openai' in provider or 'openai' in api_url.lower())):
        try:
            import openai
            api_key = llm.get('api_key')
            if not api_key:
                return ("[Error: No API key configured for this LLM]", "No explainability info available.")
            openai.api_key = api_key
            if api_url:
                openai.api_base = api_url
            model = llm.get('model', 'gpt-3.5-turbo')
            completion = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1024
            )
            response = completion.choices[0].message['content']
            explain = f"OpenAI model: {model}, prompt tokens: {completion.usage['prompt_tokens']}, completion tokens: {completion.usage['completion_tokens']}"
            return response, explain
        except Exception as e:
            return (f"[OpenAI API error: {e}]", "No explainability info available.")

    # Anthropic (Claude)
    elif (llm_type == 'api' and ('anthropic' in provider or 'anthropic' in api_url.lower())):
        try:
            import requests
            api_key = llm.get('api_key')
            if not api_key:
                return ("[Error: No API key configured for Anthropic]", "No explainability info available.")
            model = llm.get('model', 'claude-3-opus-20240229')
            anthropic_url = api_url or 'https://api.anthropic.com/v1/messages'
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }
            data = {
                'model': model,
                'max_tokens': 1024,
                'messages': [
                    {"role": "user", "content": prompt}
                ]
            }
            resp = requests.post(anthropic_url, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                content = result['content'][0]['text'] if 'content' in result and result['content'] else str(result)
                explain = f"Anthropic model: {model}, tokens used: {result.get('usage', {}).get('input_tokens', '?')}"
                return content, explain
            else:
                return (f"[Anthropic API error: {resp.status_code} {resp.text}]", "No explainability info available.")
        except Exception as e:
            return (f"[Anthropic API error: {e}]", "No explainability info available.")

    # HuggingFace Inference API
    elif (llm_type == 'api' and ('huggingface' in provider or 'huggingface' in api_url.lower())):
        try:
            import requests
            api_key = llm.get('api_key')
            if not api_key:
                return ("[Error: No API key configured for HuggingFace]", "No explainability info available.")
            model = llm.get('model', 'HuggingFaceH4/zephyr-7b-beta')
            hf_url = api_url or f'https://api-inference.huggingface.co/models/{model}'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            data = {"inputs": prompt, "parameters": {"max_new_tokens": 512}}
            resp = requests.post(hf_url, headers=headers, json=data, timeout=60)
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, list) and 'generated_text' in result[0]:
                    content = result[0]['generated_text']
                elif isinstance(result, dict) and 'generated_text' in result:
                    content = result['generated_text']
                else:
                    content = str(result)
                explain = f"HuggingFace model: {model}"
                return content, explain
            else:
                return (f"[HuggingFace API error: {resp.status_code} {resp.text}]", "No explainability info available.")
        except Exception as e:
            return (f"[HuggingFace API error: {e}]", "No explainability info available.")

    # Local LLM (transformers)
    elif llm_type == 'local':
        try:
            from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
            model_path = llm.get('path_or_url')
            if not model_path:
                return ("[Error: No local model path configured]", "No explainability info available.")
            pipe = pipeline('text-generation', model=model_path, tokenizer=model_path)
            result = pipe(prompt, max_new_tokens=512, do_sample=False)
            content = result[0]['generated_text'] if result and 'generated_text' in result[0] else str(result)
            explain = f"Local model: {model_path} (transformers pipeline)"
            return content, explain
        except ImportError:
            response = f"[transformers not installed: cannot run local LLM '{name}']\nPrompt: {prompt}\nResponse: This is a mock local LLM response."
            explain = "This output was generated by a mock local LLM. No real legal analysis was performed."
            return response, explain
        except Exception as e:
            response = f"[Local LLM error: {e}]"
            explain = "No explainability info available."
            return response, explain

    # Unknown provider/type
    else:
        response = f"[Unknown LLM type/provider: {llm_type} / {provider}]"
        explain = "No explainability info available."
        return response, explain
