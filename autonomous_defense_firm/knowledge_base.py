"""
Module for legal data sourcing, acquisition, preprocessing, and structuring.
This version is legal-practice-area-neutral and supports all law firm data types.
"""

import requests
import os
from typing import List, Dict, Any
import uuid
import json  # Ensure json is imported for JSONDecodeError handling

class KnowledgeBase:
    def __init__(self):
        # --- DATA SOURCES ---
        self.primary_sources = []
        self.secondary_sources = []
        self.tertiary_sources = []
        self.documents = []  # All documents (statutes, cases, contracts, memos, etc.)
        self.statutes = []   # Statutes only
        self.cases = []      # Cases only
        # Law firm data types (practice-area-neutral)
        self.clients = []
        self.case_files = []
        self.legal_research = []
        self.contracts = []
        self.internal_docs = []
        self.calendar_events = []
        self.notes = []
        self.feedback = []
        self.ethics_records = []
        self.financial_records = []
        self.communication_logs = []
        self.templates = []
        self.external_data = []
        # LLM management
        self.llms = []  # List of LLM configs (local/API)

    # --- ETHICAL TAGGING SUPPORT ---
    def _add_ethics_fields(self, data: dict, ethical_tags=None, ethical_guideline_ids=None):
        data = data.copy()
        if ethical_tags is not None:
            data['ethical_tags'] = ethical_tags
        if ethical_guideline_ids is not None:
            data['ethical_guideline_ids'] = ethical_guideline_ids
        return data

    # --- CRUD for documents (generic legal documents) ---
    def validate_document(self, doc: dict):
        if 'title' not in doc or 'text' not in doc:
            raise ValueError("Document must have 'title' and 'text' fields.")
        # Optionally validate ethical fields

    def create_document(self, doc: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_document(doc)
        doc = self._add_ethics_fields(doc, ethical_tags, ethical_guideline_ids)
        doc['id'] = str(uuid.uuid4())
        self.documents.append(doc)
        # TODO: Audit log: Document created with ethical tags
        return doc
    def read_document(self, doc_id: str) -> dict:
        for doc in self.documents:
            if doc.get('id') == doc_id:
                return doc
        return None
    def update_document(self, doc_id: str, updates: dict) -> bool:
        for doc in self.documents:
            if doc.get('id') == doc_id:
                self.validate_document({**doc, **updates})
                doc.update(updates)
                return True
        return False
    def delete_document(self, doc_id: str) -> bool:
        for i, doc in enumerate(self.documents):
            if doc.get('id') == doc_id:
                del self.documents[i]
                return True
        return False
    def list_documents(self, filter_type: str = None) -> list:
        if filter_type:
            return [doc for doc in self.documents if doc.get('type') == filter_type]
        return list(self.documents)

    # --- CRUD for statutes (neutral) ---
    def validate_statute(self, statute: dict):
        if 'section' not in statute or 'title' not in statute or 'text' not in statute:
            raise ValueError("Statute must have 'section', 'title', and 'text' fields.")

    def create_statute(self, statute: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_statute(statute)
        statute = self._add_ethics_fields(statute, ethical_tags, ethical_guideline_ids)
        statute['id'] = str(uuid.uuid4())
        self.statutes.append(statute)
        self.create_document({**statute, 'type': 'statute'})
        # TODO: Audit log: Statute created with ethical tags
        return statute
    def list_statutes(self) -> list:
        return list(self.statutes)
    def update_statute(self, statute_id: str, updates: dict) -> bool:
        for s in self.statutes:
            if s.get('id') == statute_id:
                self.validate_statute({**s, **updates})
                s.update(updates)
                return True
        return False

    # --- CRUD for cases (neutral) ---
    def validate_case(self, case: dict):
        if 'case_number' not in case or 'title' not in case or 'text' not in case:
            raise ValueError("Case must have 'case_number', 'title', and 'text' fields.")

    def create_case(self, case: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_case(case)
        case = self._add_ethics_fields(case, ethical_tags, ethical_guideline_ids)
        case['id'] = str(uuid.uuid4())
        self.cases.append(case)
        self.create_document({**case, 'type': 'case'})
        # TODO: Audit log: Case created with ethical tags
        return case
    def list_cases(self) -> list:
        return list(self.cases)
    def update_case(self, case_id: str, updates: dict) -> bool:
        for c in self.cases:
            if c.get('id') == case_id:
                self.validate_case({**c, **updates})
                c.update(updates)
                return True
        return False

    # --- CRUD for clients ---
    def validate_client(self, client: dict):
        if not client.get('name'):
            raise ValueError("Client must have a non-empty name.")
        if not client.get('contact'):
            raise ValueError("Client must have a contact.")

    def create_client(self, client: dict, ethical_tags=None, ethical_guideline_ids=None, vulnerability_indicator=None) -> dict:
        self.validate_client(client)
        client = self._add_ethics_fields(client, ethical_tags, ethical_guideline_ids)
        if vulnerability_indicator is not None:
            client['vulnerability_indicator'] = vulnerability_indicator
        client['id'] = str(uuid.uuid4())
        self.clients.append(client)
        # TODO: Audit log: Client created with ethical tags and vulnerability indicator
        return client
    def list_clients(self) -> list:
        return list(self.clients)
    def update_client(self, client_id: str, updates: dict):
        for client in self.clients:
            if client['id'] == client_id:
                client.update(updates)
                self.validate_client(client)
                return True
        return False
    def delete_client(self, client_id: str) -> bool:
        for i, client in enumerate(self.clients):
            if client.get('id') == client_id:
                del self.clients[i]
                return True
        return False

    # --- CRUD for case files ---
    def validate_case_file(self, case_file: dict):
        if 'title' not in case_file or 'client_id' not in case_file:
            raise ValueError("Case file must have 'title' and 'client_id' fields.")

    def create_case_file(self, case_file: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_case_file(case_file)
        case_file = self._add_ethics_fields(case_file, ethical_tags, ethical_guideline_ids)
        case_file['id'] = str(uuid.uuid4())
        self.case_files.append(case_file)
        # TODO: Audit log: Case file created with ethical tags
        return case_file
    def list_case_files(self) -> list:
        return list(self.case_files)
    def update_case_file(self, case_file_id: str, updates: dict) -> bool:
        for cf in self.case_files:
            if cf.get('id') == case_file_id:
                self.validate_case_file({**cf, **updates})
                cf.update(updates)
                return True
        return False
    def delete_case_file(self, case_file_id: str) -> bool:
        for i, cf in enumerate(self.case_files):
            if cf.get('id') == case_file_id:
                del self.case_files[i]
                return True
        return False

    # --- CRUD for legal research ---
    def validate_legal_research(self, research: dict):
        if 'topic' not in research or 'content' not in research:
            raise ValueError("Legal research must have 'topic' and 'content' fields.")

    def create_legal_research(self, research: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_legal_research(research)
        research = self._add_ethics_fields(research, ethical_tags, ethical_guideline_ids)
        research['id'] = str(uuid.uuid4())
        self.legal_research.append(research)
        # TODO: Audit log: Legal research created with ethical tags
        return research
    def list_legal_research(self) -> list:
        return list(self.legal_research)
    def update_legal_research(self, research_id: str, updates: dict) -> bool:
        for r in self.legal_research:
            if r.get('id') == research_id:
                self.validate_legal_research({**r, **updates})
                r.update(updates)
                return True
        return False
    def delete_legal_research(self, research_id: str) -> bool:
        for i, r in enumerate(self.legal_research):
            if r.get('id') == research_id:
                del self.legal_research[i]
                return True
        return False

    # --- CRUD for contracts ---
    def validate_contract(self, contract: dict):
        if 'parties' not in contract or 'effective_date' not in contract:
            raise ValueError("Contract must have 'parties' and 'effective_date' fields.")

    def create_contract(self, contract: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_contract(contract)
        contract = self._add_ethics_fields(contract, ethical_tags, ethical_guideline_ids)
        contract['id'] = str(uuid.uuid4())
        self.contracts.append(contract)
        self.create_document({**contract, 'type': 'contract'})
        # TODO: Audit log: Contract created with ethical tags
        return contract
    def list_contracts(self) -> list:
        return list(self.contracts)
    def update_contract(self, contract_id: str, updates: dict) -> bool:
        for c in self.contracts:
            if c.get('id') == contract_id:
                self.validate_contract({**c, **updates})
                c.update(updates)
                return True
        return False
    def delete_contract(self, contract_id: str) -> bool:
        for i, c in enumerate(self.contracts):
            if c.get('id') == contract_id:
                del self.contracts[i]
                return True
        return False

    # --- CRUD for internal documents ---
    def validate_internal_doc(self, doc: dict):
        if 'title' not in doc or 'content' not in doc:
            raise ValueError("Internal doc must have 'title' and 'content' fields.")

    def create_internal_doc(self, doc: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_internal_doc(doc)
        doc = self._add_ethics_fields(doc, ethical_tags, ethical_guideline_ids)
        doc['id'] = str(uuid.uuid4())
        self.internal_docs.append(doc)
        self.create_document({**doc, 'type': 'internal_doc'})
        # TODO: Audit log: Internal doc created with ethical tags
        return doc
    def list_internal_docs(self) -> list:
        return list(self.internal_docs)
    def update_internal_doc(self, doc_id: str, updates: dict) -> bool:
        for d in self.internal_docs:
            if d.get('id') == doc_id:
                self.validate_internal_doc({**d, **updates})
                d.update(updates)
                return True
        return False
    def delete_internal_doc(self, doc_id: str) -> bool:
        for i, d in enumerate(self.internal_docs):
            if d.get('id') == doc_id:
                del self.internal_docs[i]
                return True
        return False

    # --- CRUD for calendar events ---
    def validate_calendar_event(self, event: dict):
        if 'title' not in event or 'datetime' not in event or 'participants' not in event:
            raise ValueError("Calendar event must have 'title', 'datetime', and 'participants' fields.")

    def create_calendar_event(self, event: dict) -> dict:
        self.validate_calendar_event(event)
        event = event.copy()
        event['id'] = str(uuid.uuid4())
        self.calendar_events.append(event)
        return event
    def list_calendar_events(self) -> list:
        return list(self.calendar_events)
    def update_calendar_event(self, event_id: str, updates: dict) -> bool:
        for e in self.calendar_events:
            if e.get('id') == event_id:
                self.validate_calendar_event({**e, **updates})
                e.update(updates)
                return True
        return False
    def delete_calendar_event(self, event_id: str) -> bool:
        for i, e in enumerate(self.calendar_events):
            if e.get('id') == event_id:
                del self.calendar_events[i]
                return True
        return False

    # --- CRUD for notes ---
    def validate_note(self, note: dict):
        if 'author' not in note or 'body' not in note:
            raise ValueError("Note must have 'author' and 'body' fields.")

    def create_note(self, note: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_note(note)
        note = self._add_ethics_fields(note, ethical_tags, ethical_guideline_ids)
        note['id'] = str(uuid.uuid4())
        self.notes.append(note)
        # TODO: Audit log: Note created with ethical tags
        return note
    def list_notes(self) -> list:
        return list(self.notes)
    def update_note(self, note_id: str, updates: dict) -> bool:
        for n in self.notes:
            if n.get('id') == note_id:
                self.validate_note({**n, **updates})
                n.update(updates)
                return True
        return False
    def delete_note(self, note_id: str) -> bool:
        for i, n in enumerate(self.notes):
            if n.get('id') == note_id:
                del self.notes[i]
                return True
        return False

    # --- CRUD for feedback ---
    def validate_feedback(self, feedback: dict):
        if 'data_type' not in feedback or 'data' not in feedback or 'label' not in feedback:
            raise ValueError("Feedback must have 'data_type', 'data', and 'label' fields.")

    def create_feedback(self, feedback: dict) -> dict:
        self.validate_feedback(feedback)
        feedback = feedback.copy()
        feedback['id'] = str(uuid.uuid4())
        self.feedback.append(feedback)
        return feedback
    def list_feedback(self) -> list:
        return list(self.feedback)
    def update_feedback(self, feedback_id: str, updates: dict) -> bool:
        for f in self.feedback:
            if f.get('id') == feedback_id:
                self.validate_feedback({**f, **updates})
                f.update(updates)
                return True
        return False
    def delete_feedback(self, feedback_id: str) -> bool:
        for i, f in enumerate(self.feedback):
            if f.get('id') == feedback_id:
                del self.feedback[i]
                return True
        return False

    # --- CRUD for ethics records ---
    def validate_ethics_record(self, record: dict):
        if 'issue' not in record or 'date' not in record or 'resolution' not in record:
            raise ValueError("Ethics record must have 'issue', 'date', and 'resolution' fields.")

    def create_ethics_record(self, record: dict) -> dict:
        self.validate_ethics_record(record)
        record = record.copy()
        record['id'] = str(uuid.uuid4())
        self.ethics_records.append(record)
        return record
    def list_ethics_records(self) -> list:
        return list(self.ethics_records)
    def update_ethics_record(self, record_id: str, updates: dict) -> bool:
        for r in self.ethics_records:
            if r.get('id') == record_id:
                self.validate_ethics_record({**r, **updates})
                r.update(updates)
                return True
        return False
    def delete_ethics_record(self, record_id: str) -> bool:
        for i, r in enumerate(self.ethics_records):
            if r.get('id') == record_id:
                del self.ethics_records[i]
                return True
        return False

    # --- CRUD for financial records ---
    def validate_financial_record(self, record: dict):
        if 'amount' not in record or 'date' not in record or 'description' not in record:
            raise ValueError("Financial record must have 'amount', 'date', and 'description' fields.")

    def create_financial_record(self, record: dict) -> dict:
        self.validate_financial_record(record)
        record = record.copy()
        record['id'] = str(uuid.uuid4())
        self.financial_records.append(record)
        return record
    def list_financial_records(self) -> list:
        return list(self.financial_records)
    def update_financial_record(self, record_id: str, updates: dict) -> bool:
        for r in self.financial_records:
            if r.get('id') == record_id:
                self.validate_financial_record({**r, **updates})
                r.update(updates)
                return True
        return False
    def delete_financial_record(self, record_id: str) -> bool:
        for i, r in enumerate(self.financial_records):
            if r.get('id') == record_id:
                del self.financial_records[i]
                return True
        return False

    # --- CRUD for communication logs ---
    def validate_communication_log(self, log: dict):
        if 'participants' not in log or 'timestamp' not in log or 'content' not in log:
            raise ValueError("Communication log must have 'participants', 'timestamp', and 'content' fields.")

    def create_communication_log(self, log: dict) -> dict:
        self.validate_communication_log(log)
        log = log.copy()
        log['id'] = str(uuid.uuid4())
        self.communication_logs.append(log)
        return log
    def list_communication_logs(self) -> list:
        return list(self.communication_logs)
    def update_communication_log(self, log_id: str, updates: dict) -> bool:
        for l in self.communication_logs:
            if l.get('id') == log_id:
                self.validate_communication_log({**l, **updates})
                l.update(updates)
                return True
        return False
    def delete_communication_log(self, log_id: str) -> bool:
        for i, l in enumerate(self.communication_logs):
            if l.get('id') == log_id:
                del self.communication_logs[i]
                return True
        return False

    # --- CRUD for templates ---
    def validate_template(self, template: dict):
        if 'name' not in template or 'content' not in template:
            raise ValueError("Template must have 'name' and 'content' fields.")

    def create_template(self, template: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_template(template)
        template = self._add_ethics_fields(template, ethical_tags, ethical_guideline_ids)
        template['id'] = str(uuid.uuid4())
        self.templates.append(template)
        # TODO: Audit log: Template created with ethical tags
        return template
    def list_templates(self) -> list:
        return list(self.templates)
    def update_template(self, template_id: str, updates: dict) -> bool:
        for t in self.templates:
            if t.get('id') == template_id:
                self.validate_template({**t, **updates})
                t.update(updates)
                return True
        return False
    def delete_template(self, template_id: str) -> bool:
        for i, t in enumerate(self.templates):
            if t.get('id') == template_id:
                del self.templates[i]
                return True
        return False

    # --- CRUD for external data ---
    def validate_external_data(self, data: dict):
        if 'source' not in data or 'content' not in data:
            raise ValueError("External data must have 'source' and 'content' fields.")

    def create_external_data(self, data: dict, ethical_tags=None, ethical_guideline_ids=None) -> dict:
        self.validate_external_data(data)
        data = self._add_ethics_fields(data, ethical_tags, ethical_guideline_ids)
        data['id'] = str(uuid.uuid4())
        self.external_data.append(data)
        # TODO: Audit log: External data created with ethical tags
        return data

    # --- LLM management (local and API) ---
    def validate_llm(self, llm: dict):
        if 'name' not in llm or 'type' not in llm:
            raise ValueError("LLM config must have 'name' and 'type'.")
        if llm['type'] == 'local':
            if 'model_path' not in llm: # Original had model_path, new model has path_or_url
                raise ValueError("Local LLM config must have 'model_path'.")
        elif llm['type'] == 'api':
            if 'api_url' not in llm or 'api_key' not in llm: # Original had api_url and api_key
                raise ValueError("API LLM config must have 'api_url' and 'api_key'.")
        else:
            raise ValueError("LLM type must be 'local' or 'api'.")

    def create_llm(self, llm: dict) -> dict:
        # This method is for the in-memory list, the webapp uses DB.
        # Validation might differ slightly if field names changed (e.g. model_path vs path_or_url)
        custom_llm_validation = llm.copy()
        if 'path_or_url' in custom_llm_validation and 'model_path' not in custom_llm_validation and custom_llm_validation['type'] == 'local':
            custom_llm_validation['model_path'] = custom_llm_validation['path_or_url']
        if 'path_or_url' in custom_llm_validation and 'api_url' not in custom_llm_validation and custom_llm_validation['type'] == 'api':
             custom_llm_validation['api_url'] = custom_llm_validation['path_or_url']
        
        self.validate_llm(custom_llm_validation) # Use validated copy
        
        llm_to_add = llm.copy() # Work with original field names for internal list
        llm_to_add['id'] = str(uuid.uuid4())
        if 'is_default' not in llm_to_add:
            llm_to_add['is_default'] = False
        self.llms.append(llm_to_add)
        return llm_to_add

    def list_llms(self) -> list:
        return list(self.llms)

    def update_llm(self, llm_id: str, updates: dict) -> bool:
        for llm_obj in self.llms:
            if llm_obj.get('id') == llm_id:
                # Similar validation adaptation as in create_llm
                prospective_update = {**llm_obj, **updates}
                if 'path_or_url' in prospective_update and 'model_path' not in prospective_update and prospective_update['type'] == 'local':
                    prospective_update['model_path'] = prospective_update['path_or_url']
                if 'path_or_url' in prospective_update and 'api_url' not in prospective_update and prospective_update['type'] == 'api':
                    prospective_update['api_url'] = prospective_update['path_or_url']

                self.validate_llm(prospective_update)
                llm_obj.update(updates)
                return True
        return False

    def delete_llm(self, llm_id: str) -> bool:
        for i, llm_obj in enumerate(self.llms):
            if llm_obj.get('id') == llm_id:
                del self.llms[i]
                return True
        return False

    def set_default_llm(self, llm_id: str) -> bool:
        found = False
        for llm_obj in self.llms:
            if llm_obj.get('id') == llm_id:
                llm_obj['is_default'] = True
                found = True
            else:
                llm_obj['is_default'] = False
        return found

    def get_default_llm(self) -> dict:
        for llm_obj in self.llms:
            if llm_obj.get('is_default'):
                return llm_obj
        return None

    # --- CRUD for users (with roles and password hashing) ---
    def validate_user(self, user: dict):
        if 'username' not in user or not user['username']:
            raise ValueError("User must have a non-empty 'username'.")
        if 'role' not in user or user['role'] not in ['admin', 'lawyer', 'staff', 'client']:
            raise ValueError("User must have a valid 'role' (admin, lawyer, staff, client).")
        if 'password_hash' not in user or not user['password_hash']:
            raise ValueError("User must have a password hash.")

    def _hash_password(self, password: str) -> str:
        import hashlib, os
        salt = os.urandom(16)
        hash_ = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ':' + hash_.hex()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        import hashlib
        salt_hex, hash_hex = password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        hash_ = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hash_.hex() == hash_hex

    def create_user(self, user: dict, password: str) -> dict:
        if not hasattr(self, 'users'):
            self.users = []
        user = user.copy()
        user['id'] = str(uuid.uuid4())
        user['password_hash'] = self._hash_password(password)
        self.validate_user(user)
        self.users.append(user)
        # TODO: Audit log: User created
        return user

    def list_users(self) -> list:
        if not hasattr(self, 'users'):
            self.users = []
        return list(self.users)

    def get_user_by_username(self, username: str) -> dict | None:
        if not hasattr(self, 'users'):
            self.users = []
        for u in self.users:
            if u.get('username') == username:
                return u
        return None

    def update_user(self, user_id: str, updates: dict) -> bool:
        if not hasattr(self, 'users'):
            self.users = []
        for u in self.users:
            if u.get('id') == user_id:
                # Prevent username/id from being updated
                updates = {k: v for k, v in updates.items() if k not in ['id', 'username']}
                u.update(updates)
                self.validate_user(u)
                # TODO: Audit log: User updated
                return True
        return False

    def delete_user(self, user_id: str) -> bool:
        if not hasattr(self, 'users'):
            self.users = []
        for i, u in enumerate(self.users):
            if u.get('id') == user_id:
                del self.users[i]
                # TODO: Audit log: User deleted
                return True
        return False

    def authenticate_user(self, username: str, password: str) -> dict | None:
        user = self.get_user_by_username(username)
        if user and self._verify_password(password, user['password_hash']):
            return user
        return None

    def ingest_document(self, doc):
        self.create_document(doc)

    def preprocess(self):
        pass

    def fetch_caselaw_access_project(self, court: str = "tn", page_size: int = 20, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches opinions from the Caselaw Access Project API for a given court (default: Tennessee).
        Returns a list of opinions (dicts).
        """
        url = f"https://api.case.law/v1/cases/"
        params = {
            "court": court,
            "page_size": page_size,
            "page": 1 # Start with page 1
        }
        opinions = []
        current_page = 1
        while current_page <= max_pages:
            params["page"] = current_page
            try:
                resp = requests.get(url, params=params, timeout=10) # Added timeout
                resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                data = resp.json()
                opinions.extend(data.get("results", []))
                if not data.get("next"): # Check if there's a next page
                    break 
            except requests.exceptions.RequestException as e:
                print(f"[Error] Request to Caselaw Access Project failed: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"[Error] Could not parse JSON from Caselaw Access Project: {e}")
                print(f"Response content: {resp.text[:500] if resp else 'No response'}")
                break
            current_page +=1
        return opinions

    def fetch_courtlistener(self, jurisdiction: str = "tenn", page_size: int = 20, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches opinions from CourtListener API for a given jurisdiction (default: Tennessee).
        Returns a list of opinions (dicts).
        """
        url = "https://www.courtlistener.com/api/rest/v3/opinions/"
        params = {
            "jurisdiction": jurisdiction,
            "page_size": page_size,
            "page": 1 # Start with page 1
        }
        opinions = []
        current_page = 1
        while current_page <= max_pages:
            params["page"] = current_page
            try:
                resp = requests.get(url, params=params, timeout=10) # Added timeout
                resp.raise_for_status()
                data = resp.json()
                opinions.extend(data.get("results", []))
                if not data.get("next"): # Check if there's a next page
                    break
            except requests.exceptions.RequestException as e:
                print(f"[Error] Request to CourtListener failed: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"[Error] Could not parse JSON from CourtListener: {e}")
                print(f"Response content: {resp.text[:500] if resp else 'No response'}")
                break
            current_page += 1
        return opinions
        
    def save_to_gcloud(self, data: List[Dict[str, Any]], bucket_name: str, filename: str) -> bool:
        """
        Saves the given data to a Google Cloud Storage bucket as a JSON file.
        Requires the GOOGLE_APPLICATION_CREDENTIALS env variable to be set.
        """
        try:
            from google.cloud import storage # Import moved here
            import json # Import moved here
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(json.dumps(data), content_type='application/json')
            print(f"[GCloud] Successfully saved to {bucket_name}/{filename}")
            return True
        except ImportError:
            print("[GCloud Error] google-cloud-storage library not found. Please install it.")
            return False
        except Exception as e:
            print(f"[GCloud Error] {e}")
            return False

    def human_review(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Allows a human to review and approve/reject each item in the data list.
        Returns a list of approved items.
        """
        approved = []
        if not data: # Handle empty data
            return approved
            
        for item in data:
            print("\n--- Legal Document Preview ---")
            # Attempt to find a name or use a snippet
            preview_name = item.get("caseName") or item.get("case_name") or item.get("title")
            if preview_name:
                print(preview_name)
            else:
                print(str(item)[:500]) # Fallback to raw snippet
            print("-----------------------------")
            
            while True: # Loop for valid input
                resp = input("Approve this document? (y/n): ").strip().lower()
                if resp in ['y', 'n']:
                    break
                print("Invalid input. Please enter 'y' or 'n'.")

            if resp == 'y':
                approved.append(item)
        return approved

    def fetch_tn_statutes_justia(self, max_sections: int = 10) -> list:
        """
        Fetches Tennessee statutes from Justia (public domain, HTML scraping).
        Returns a list of statute dicts (section, title, text).
        Requires 'beautifulsoup4' (bs4) to be installed.
        """
        try:
            from bs4 import BeautifulSoup # Import moved here
        except ImportError:
            print("[Error] beautifulsoup4 is not installed. Please install with 'pip install beautifulsoup4'.")
            return []
        
        base_url = "https://law.justia.com/codes/tennessee/2021/title-39/" # Using 2021 as example
        statutes = []
        
        # Assuming sections are consecutively numbered chapters for this example
        # This part is highly dependent on Justia's URL structure for TN statutes
        # For Title 39, it seems to be chapter-based.
        # Example: https://law.justia.com/codes/tennessee/2021/title-39/chapter-11/
        # We'd need a way to discover valid chapter numbers or a different approach.
        # The original code iterates `section` from 1 to max_sections and appends to base_url
        # This might not align with how Justia structures its URLs for TN statutes (title/chapter/part/section)
        # For simplicity, I'll keep the loop but acknowledge it might need adjustment for real TN statutes.

        print(f"[Info] Attempting to fetch up to {max_sections} sections/chapters from {base_url}...")
        # This loop assumes 'section' maps to a chapter or a main page for that number in the URL.
        for section_num in range(1, max_sections + 1): 
            # This URL construction might need to be more specific (e.g., targeting chapters or specific sections)
            # For example, if 'section' refers to chapters:
            url = f"{base_url}chapter-{section_num}/" 
            # Or if it refers to a generic section index page (less likely for Justia's deep links)
            # url = f"{base_url}{section_num}/" # Original assumption

            print(f"[Info] Fetching {url}")
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Extracting title: Justia's structure can vary.
                # This is a generic attempt; specific selectors are usually needed.
                title_tag = soup.find('h1') or soup.find('h2') # Common title tags
                title = title_tag.text.strip() if title_tag else f"Tennessee Code - Title 39 - Chapter/Section {section_num}"
                
                # Extracting text: This is also generic.
                # Often, legal text is within specific divs or <p> tags with certain classes.
                text_content = []
                # Look for a main content area if possible
                main_content_div = soup.find('div', class_='law-text-content') # Example class
                if main_content_div:
                    paragraphs = main_content_div.find_all('p')
                else: # Fallback to all p tags if no specific content div
                    paragraphs = soup.find_all('p')

                for p in paragraphs:
                    text_content.append(p.get_text(separator='\n', strip=True))
                
                full_text = '\n'.join(text_content)

                if not full_text: # If no text found, maybe it was just a listing page
                    print(f"[Warning] No text content found for {url}. It might be an index page or the structure changed.")
                    continue

                statutes.append({"section_number": str(section_num), "title": title, "text": full_text, "source_url": url})
                if len(statutes) >= max_sections: # Control how many actual statutes are collected
                    break

            except requests.exceptions.RequestException as e:
                print(f"[Error] Could not fetch {url}: {e}")
                # Continue to next section if one fails, or break if too many failures
            except Exception as e:
                print(f"[Error] Error parsing {url}: {e}")
        
        print(f"[Info] Fetched {len(statutes)} statutes.")
        return statutes

    def fetch_us_constitution(self) -> list:
        """
        Fetches the U.S. Constitution from the National Archives website (amendments page).
        Returns a list of articles and amendments (title, text).
        """
        # URL for amendments 11-27
        url_amendments_11_27 = "https://www.archives.gov/founding-docs/amendments-11-27"
        # URL for Bill of Rights (Amendments 1-10)
        url_bill_of_rights = "https://www.archives.gov/founding-docs/bill-of-rights-transcript"
        # URL for the Constitution itself (Articles)
        url_articles = "https://www.archives.gov/founding-docs/constitution-transcript"

        constitution_parts = []
        
        try:
            from bs4 import BeautifulSoup # Import moved here
        except ImportError:
            print("[Error] beautifulsoup4 is not installed. Please install with 'pip install beautifulsoup4'.")
            return []

        sources_to_fetch = {
            "Articles": url_articles,
            "Bill of Rights": url_bill_of_rights,
            "Amendments 11-27": url_amendments_11_27,
        }

        for part_name, url in sources_to_fetch.items():
            print(f"[Info] Fetching {part_name} from {url}...")
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Scraping logic is highly dependent on the specific page structure of archives.gov
                # This needs to be robust and adaptable. The class 'field-item even' might not be universal.
                # For a more robust solution, one might need different selectors for articles vs. amendments.

                if "constitution-transcript" in url: # Articles
                    # Structure for articles is often different, e.g., `<h2>Article. I.</h2><p>Section. 1.</p>`
                    # This is a simplified example; actual parsing would be more complex.
                    article_elements = soup.select('h2, h3, p') # Basic tags for articles
                    current_title = part_name
                    current_text = []
                    for element in article_elements:
                        if element.name in ['h2', 'h3']: # New article or major section
                            if current_text: # Save previous article's text
                                constitution_parts.append({"title": current_title, "text": '\n'.join(current_text).strip(), "source": url})
                                current_text = []
                            current_title = element.get_text(strip=True)
                        elif element.name == 'p':
                            current_text.append(element.get_text(strip=True))
                    if current_text: # Append the last collected text
                         constitution_parts.append({"title": current_title, "text": '\n'.join(current_text).strip(), "source": url})


                else: # Amendments (Bill of Rights & 11-27)
                    # The original code used 'div.field-item.even', this might be specific to one page.
                    # Let's try a more general approach if that fails.
                    content_blocks = soup.find_all('div', class_='field--name-field-historical-description') # Common on archives.gov
                    if not content_blocks: # Fallback if the above class isn't found
                        content_blocks = soup.select('article p, article h3') # Generic content selectors

                    for block in content_blocks:
                        title_tag = block.find('h3') or block.find('h2') # Amendment titles often in h3
                        title = title_tag.get_text(strip=True) if title_tag else part_name # Fallback title

                        # Get all paragraphs within this block
                        text_elements = block.find_all('p')
                        text = '\n'.join([p.get_text(strip=True) for p in text_elements if p.get_text(strip=True)])
                        
                        if text: # Only add if text was found
                            constitution_parts.append({"title": title, "text": text, "source": url})
            
            except requests.exceptions.RequestException as e:
                print(f"[Error] Could not fetch {url}: {e}")
            except Exception as e:
                print(f"[Error] Error parsing {url}: {e}")

        print(f"[Info] Fetched {len(constitution_parts)} parts of the Constitution.")
        return constitution_parts

    def fetch_case_law_data(self, court_jurisdiction: str = "Tennessee", max_pages_per_source: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches case law data from various sources for a given court/jurisdiction.
        Returns a merged list of case law records.
        The 'court_jurisdiction' parameter should be mapped to specific API parameters.
        """
        all_data = []
        
        # Map general "Tennessee" to specific API params
        cap_court_param = "tn" # Default for Caselaw Access Project if 'Tennessee'
        cl_jurisdiction_param = "tenn" # Default for CourtListener if 'Tennessee'

        # Basic mapping (can be expanded)
        if court_jurisdiction.lower() == "federal":
            cap_court_param = "scotus" # Example: Supreme Court for CAP
            cl_jurisdiction_param = "us"   # Example: All federal for CourtListener
        # Add more sophisticated mapping if needed based on input `court_jurisdiction`

        print(f"[Info] Fetching from Caselaw Access Project for court param: '{cap_court_param}'...")
        cap_data = self.fetch_caselaw_access_project(court=cap_court_param, max_pages=max_pages_per_source)
        if cap_data:
            for item in cap_data: item['data_source'] = 'Caselaw Access Project' # Tag source
            all_data.extend(cap_data)
        print(f"[Info] Fetched {len(cap_data)} records from CAP.")

        print(f"[Info] Fetching from CourtListener for jurisdiction param: '{cl_jurisdiction_param}'...")
        cl_data = self.fetch_courtlistener(jurisdiction=cl_jurisdiction_param, max_pages=max_pages_per_source)
        if cl_data:
            for item in cl_data: item['data_source'] = 'CourtListener' # Tag source
            all_data.extend(cl_data)
        print(f"[Info] Fetched {len(cl_data)} records from CourtListener.")
        
        print(f"[Info] Total case law records fetched: {len(all_data)}.")
        return all_data

    def fetch_and_store_case_law(self, court_jurisdiction: str = "Tennessee", bucket_name: str = "your-bucket-name", max_pages_per_source: int = 5, auto_approve_review: bool = False):
        """
        Fetches case law data and stores it in a Google Cloud Storage bucket.
        """
        print(f"\n--- Starting Case Law Fetch & Store for: {court_jurisdiction} ---")
        data = self.fetch_case_law_data(court_jurisdiction=court_jurisdiction, max_pages_per_source=max_pages_per_source)
        if not data:
            print("[Warning] No case law data found to store.")
            return

        # Standardize filename based on jurisdiction
        filename_court_jurisdiction = court_jurisdiction.lower().replace(" ", "_")
        raw_filename = f"case_law/{filename_court_jurisdiction}/raw_data_{uuid.uuid4().hex[:8]}.json"
        approved_filename = f"case_law/{filename_court_jurisdiction}/approved_data_{uuid.uuid4().hex[:8]}.json"

        print(f"[Info] Saving raw data to GCS: {bucket_name}/{raw_filename}")
        if self.save_to_gcloud(data, bucket_name, raw_filename):
             print("[Info] Raw data saved successfully.")
        else:
            print("[Error] Failed to save raw data to GCS.")

        print("[Info] Starting human review process for fetched case law...")
        if auto_approve_review:
            print("[Info] Auto-approving all items for review (debug/testing mode).")
            approved_data = data # In auto-approve, all data is "approved"
        else:
            approved_data = self.human_review(data)
        
        if approved_data:
            print(f"[Info] {len(approved_data)} items approved. Saving approved data to GCS: {bucket_name}/{approved_filename}")
            if self.save_to_gcloud(approved_data, bucket_name, approved_filename):
                print("[Info] Approved data saved successfully.")
            else:
                print("[Error] Failed to save approved data to GCS.")
        else:
            print("[Info] No data was approved during human review.")
        print("--- Case Law Fetch & Store Completed ---")


    def fetch_statutes_and_store(self, jurisdiction: str = "Tennessee", max_items: int = 10, bucket_name: str = "your-bucket-name", auto_approve_review: bool = False):
        """
        Fetches statutes (e.g. TN from Justia) and stores them in GCS.
        'max_items' refers to max_sections for Justia TN.
        """
        print(f"\n--- Starting Statute Fetch & Store for: {jurisdiction} ---")
        statutes = []
        if jurisdiction.lower() in ["tennessee", "tn"]:
            print(f"[Info] Fetching Tennessee statutes from Justia (max_sections={max_items})...")
            statutes = self.fetch_tn_statutes_justia(max_sections=max_items)
        else:
            print(f"[Warning] Statute fetching for '{jurisdiction}' is not implemented beyond Tennessee/Justia in this version.")
            return

        if not statutes:
            print(f"[Warning] No statutes found for {jurisdiction} to store.")
            return

        filename_jurisdiction = jurisdiction.lower().replace(" ", "_")
        raw_filename = f"statutes/{filename_jurisdiction}/raw_data_{uuid.uuid4().hex[:8]}.json"
        approved_filename = f"statutes/{filename_jurisdiction}/approved_data_{uuid.uuid4().hex[:8]}.json"

        print(f"[Info] Saving raw statutes to GCS: {bucket_name}/{raw_filename}")
        if self.save_to_gcloud(statutes, bucket_name, raw_filename):
            print("[Info] Raw statutes saved successfully.")
        else:
            print("[Error] Failed to save raw statutes to GCS.")
        
        print("[Info] Starting human review process for fetched statutes...")
        if auto_approve_review:
            print("[Info] Auto-approving all items for review (debug/testing mode).")
            approved_statutes = statutes
        else:
            approved_statutes = self.human_review(statutes)

        if approved_statutes:
            print(f"[Info] {len(approved_statutes)} statutes approved. Saving to GCS: {bucket_name}/{approved_filename}")
            if self.save_to_gcloud(approved_statutes, bucket_name, approved_filename):
                print("[Info] Approved statutes saved successfully.")
            else:
                print("[Error] Failed to save approved statutes to GCS.")
        else:
            print("[Info] No statutes were approved during human review.")
        print("--- Statute Fetch & Store Completed ---")


    def run_pipeline(self, court_jurisdiction: str = "Tennessee", max_case_pages_per_source: int = 5, 
                     statute_jurisdiction: str = "Tennessee", max_statute_items: int = 10, 
                     bucket_name: str = "your-bucket-name", auto_approve_review: bool = False):
        """
        Runs the data fetching pipeline: fetches case law, fetches statutes, and stores both in Google Cloud Storage.
        """
        print("\n===== Starting Data Ingestion Pipeline =====")
        self.fetch_and_store_case_law(
            court_jurisdiction=court_jurisdiction, 
            bucket_name=bucket_name, 
            max_pages_per_source=max_case_pages_per_source,
            auto_approve_review=auto_approve_review
        )
        self.fetch_statutes_and_store(
            jurisdiction=statute_jurisdiction, 
            max_items=max_statute_items, 
            bucket_name=bucket_name,
            auto_approve_review=auto_approve_review
        )
        # Could add Constitution fetching here too if desired
        # print("[Info] Fetching US Constitution...")
        # constitution_data = self.fetch_us_constitution()
        # if constitution_data:
        #     self.save_to_gcloud(constitution_data, bucket_name, f"constitutions/us_constitution_{uuid.uuid4().hex[:8]}.json")
        # else:
        #     print("[Warning] No constitution data fetched.")
        print("===== Data Ingestion Pipeline Completed =====")


    def test_integration(self, bucket_name_to_use="kb-integration-test-bucket"):
        """
        Runs a full integration test: fetch case law, fetch statutes, and store in GCloud.
        Uses small limits for quick testing.
        """
        print("\n===== Starting Integration Test =====")
        # Note: For real tests, ensure the bucket_name_to_use exists and you have permissions.
        # Using auto_approve_review = True to avoid needing user input during automated tests.
        self.run_pipeline(
            court_jurisdiction="Tennessee", 
            max_case_pages_per_source=1, # Small number for testing
            statute_jurisdiction="Tennessee",
            max_statute_items=1, # Small number for testing
            bucket_name=bucket_name_to_use,
            auto_approve_review=True 
        )
        print("===== Integration Test Completed =====")
        print(f"IMPORTANT: Check bucket '{bucket_name_to_use}' for test artifacts and clean up if necessary.")


    # --- Debugging versions of fetch methods ---
    def debug_fetch_caselaw_access_project(self, court: str = "tn", page_size: int = 1, max_pages: int = 1): # smaller defaults for debug
        """ Debugging version: prints requests and responses from Caselaw Access Project. """
        url = f"https://api.case.law/v1/cases/"
        params = {"court": court, "page_size": page_size}
        opinions = []
        for page_num in range(1, max_pages + 1):
            params["page"] = page_num
            print(f"[DEBUG CAP] Requesting: {url} with params {params}")
            try:
                resp = requests.get(url, params=params, timeout=10)
                print(f"[DEBUG CAP] Response Status: {resp.status_code}")
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                print(f"[DEBUG CAP] Fetched {len(results)} records from page {page_num}.")
                # print(f"[DEBUG CAP] Sample record: {results[0] if results else 'No results'}")
                opinions.extend(results)
                if not data.get("next"):
                    print("[DEBUG CAP] No more pages.")
                    break
            except requests.exceptions.RequestException as e:
                print(f"[DEBUG CAP Error] Request failed: {e}")
                if resp: print(f"[DEBUG CAP Error] Response content: {resp.text[:500]}")
                break
            except json.JSONDecodeError as e:
                print(f"[DEBUG CAP Error] JSON Parse failed: {e}")
                print(f"[DEBUG CAP Error] Response content: {resp.text[:500]}")
                break
        return opinions

    def debug_fetch_courtlistener(self, jurisdiction: str = "tenn", page_size: int = 1, max_pages: int = 1): # smaller defaults
        """ Debugging version: prints requests and responses from CourtListener. """
        url = "https://www.courtlistener.com/api/rest/v3/opinions/"
        params = {"jurisdiction": jurisdiction, "page_size": page_size}
        opinions = []
        for page_num in range(1, max_pages + 1):
            params["page"] = page_num
            print(f"[DEBUG CL] Requesting: {url} with params {params}")
            try:
                resp = requests.get(url, params=params, timeout=10)
                print(f"[DEBUG CL] Response Status: {resp.status_code}")
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                print(f"[DEBUG CL] Fetched {len(results)} records from page {page_num}.")
                # print(f"[DEBUG CL] Sample record: {results[0] if results else 'No results'}")
                opinions.extend(results)
                if not data.get("next"):
                    print("[DEBUG CL] No more pages.")
                    break
            except requests.exceptions.RequestException as e:
                print(f"[DEBUG CL Error] Request failed: {e}")
                if resp: print(f"[DEBUG CL Error] Response content: {resp.text[:500]}")
                break
            except json.JSONDecodeError as e:
                print(f"[DEBUG CL Error] JSON Parse failed: {e}")
                print(f"[DEBUG CL Error] Response content: {resp.text[:500]}")
                break
        return opinions

    def debug_save_to_gcloud(self, data: List[Dict[str, Any]], bucket_name: str, filename: str):
        """ Debugging version: prints data and parameters before attempting to save to GCloud. """
        print(f"[DEBUG GCloud] Attempting to save {len(data)} records to bucket '{bucket_name}' as '{filename}'.")
        if data:
            print(f"[DEBUG GCloud] First item sample: {data[0]}")
        else:
            print("[DEBUG GCloud] No data to save.")
        # Actual save call
        self.save_to_gcloud(data, bucket_name, filename)

    def debug_human_review(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ Debugging version: auto-approves all items for human review. """
        print("[DEBUG Review] Starting debug human review (auto-approving all).")
        if not data: return []
        for item in data:
            preview_name = item.get("caseName") or item.get("case_name") or item.get("title", "Unknown Title")
            print(f"[DEBUG Review] Auto-approving: {preview_name[:100]}")
        print(f"[DEBUG Review] Auto-approved {len(data)} items.")
        return list(data) # Return a copy

    def run_debug_pipeline(self, court_jurisdiction: str = "Tennessee", max_case_pages_per_source: int = 1, 
                           statute_jurisdiction: str = "Tennessee", max_statute_items: int = 1, 
                           bucket_name: str = "your-debug-bucket"):
        """ Runs the pipeline in debug mode with verbose output and auto-approvals. """
        print("\n===== Starting Data Ingestion Pipeline (DEBUG MODE) =====")
        
        # Debug Case Law Fetch & Store
        print(f"\n--- Debug Case Law Fetch & Store for: {court_jurisdiction} ---")
        # Use debug fetch methods
        cap_court_param = "tn" if court_jurisdiction.lower() == "tennessee" else court_jurisdiction.lower()
        cl_jurisdiction_param = "tenn" if court_jurisdiction.lower() == "tennessee" else court_jurisdiction.lower()

        print(f"[DEBUG Pipeline] Fetching from Caselaw Access Project (court: {cap_court_param})...")
        cap_data = self.debug_fetch_caselaw_access_project(court=cap_court_param, max_pages=max_case_pages_per_source)
        print(f"[DEBUG Pipeline] Fetching from CourtListener (jurisdiction: {cl_jurisdiction_param})...")
        cl_data = self.debug_fetch_courtlistener(jurisdiction=cl_jurisdiction_param, max_pages=max_case_pages_per_source)
        
        all_case_data = []
        if cap_data: all_case_data.extend(cap_data)
        if cl_data: all_case_data.extend(cl_data)

        if not all_case_data:
            print("[DEBUG Pipeline Warning] No case law data found.")
        else:
            filename_court = court_jurisdiction.lower().replace(" ", "_")
            raw_fn = f"case_law/{filename_court}/DEBUG_raw_data_{uuid.uuid4().hex[:8]}.json"
            approved_fn = f"case_law/{filename_court}/DEBUG_approved_data_{uuid.uuid4().hex[:8]}.json"
            self.debug_save_to_gcloud(all_case_data, bucket_name, raw_fn)
            approved_case_data = self.debug_human_review(all_case_data)
            if approved_case_data:
                self.debug_save_to_gcloud(approved_case_data, bucket_name, approved_fn)
        print("--- Debug Case Law Fetch & Store Completed ---")

        # Debug Statute Fetch & Store
        print(f"\n--- Debug Statute Fetch & Store for: {statute_jurisdiction} ---")
        statutes = []
        if statute_jurisdiction.lower() in ["tennessee", "tn"]:
            print(f"[DEBUG Pipeline] Fetching TN statutes from Justia (max_sections={max_statute_items})...")
            # Assuming fetch_tn_statutes_justia also has sufficient internal logging or can be wrapped.
            statutes = self.fetch_tn_statutes_justia(max_sections=max_statute_items) 
        else:
            print(f"[DEBUG Pipeline Warning] Statute fetching for '{statute_jurisdiction}' not implemented beyond TN.")

        if not statutes:
            print(f"[DEBUG Pipeline Warning] No statutes found for {statute_jurisdiction}.")
        else:
            filename_statute = statute_jurisdiction.lower().replace(" ", "_")
            raw_fn_stat = f"statutes/{filename_statute}/DEBUG_raw_data_{uuid.uuid4().hex[:8]}.json"
            approved_fn_stat = f"statutes/{filename_statute}/DEBUG_approved_data_{uuid.uuid4().hex[:8]}.json"
            self.debug_save_to_gcloud(statutes, bucket_name, raw_fn_stat)
            approved_statutes = self.debug_human_review(statutes)
            if approved_statutes:
                self.debug_save_to_gcloud(approved_statutes, bucket_name, approved_fn_stat)
        print("--- Debug Statute Fetch & Store Completed ---")
        
        print("===== Data Ingestion Pipeline (DEBUG MODE) Completed =====")
        print(f"IMPORTANT: Check bucket '{bucket_name}' for DEBUG test artifacts and clean up if necessary.")

    # --- Persistence methods for backup/restore of the in-memory KB ---
    # These are for the CLI's original design. The web app MVP uses its own DB backup.
    def save_to_file(self, filename: str):
        import json # Import moved here
        # Consolidate all data into a dictionary
        data_to_save = {
            'primary_sources': self.primary_sources,
            'secondary_sources': self.secondary_sources,
            'tertiary_sources': self.tertiary_sources,
            'documents': self.documents,
            'statutes': self.statutes,
            'cases': self.cases,
            'clients': self.clients,
            'case_files': self.case_files,
            'legal_research': self.legal_research,
            'contracts': self.contracts,
            'internal_docs': self.internal_docs,
            'calendar_events': self.calendar_events,
            'notes': self.notes,
            'feedback': self.feedback,
            'ethics_records': self.ethics_records,
            'financial_records': self.financial_records,
            'communication_logs': self.communication_logs,
            'templates': self.templates,
            'external_data': self.external_data,
            'llms': self.llms, # LLM configurations
            'profiles': getattr(self, 'profiles', []), # User/Case Profiles
            'active_profile_id': getattr(self, 'active_profile_id', None)
        }
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4) # Using indent for readability
            print(f"[KB Save] KnowledgeBase state saved to {filename}")
        except IOError as e:
            print(f"[KB Save Error] Could not write to file {filename}: {e}")
        except TypeError as e:
            print(f"[KB Save Error] Data is not JSON serializable: {e}")


    def load_from_file(self, filename: str):
        import json # Import moved here
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data_loaded = json.load(f)

            # Assign to attributes, using .get for safety with default empty lists/None
            self.primary_sources = data_loaded.get('primary_sources', [])
            self.secondary_sources = data_loaded.get('secondary_sources', [])
            self.tertiary_sources = data_loaded.get('tertiary_sources', [])
            self.documents = data_loaded.get('documents', [])
            self.statutes = data_loaded.get('statutes', [])
            self.cases = data_loaded.get('cases', [])
            self.clients = data_loaded.get('clients', [])
            self.case_files = data_loaded.get('case_files', [])
            self.legal_research = data_loaded.get('legal_research', [])
            self.contracts = data_loaded.get('contracts', [])
            self.internal_docs = data_loaded.get('internal_docs', [])
            self.calendar_events = data_loaded.get('calendar_events', [])
            self.notes = data_loaded.get('notes', [])
            self.feedback = data_loaded.get('feedback', [])
            self.ethics_records = data_loaded.get('ethics_records', [])
            self.financial_records = data_loaded.get('financial_records', [])
            self.communication_logs = data_loaded.get('communication_logs', [])
            self.templates = data_loaded.get('templates', [])
            self.external_data = data_loaded.get('external_data', [])
            self.llms = data_loaded.get('llms', [])
            
            # Profile related attributes
            self.profiles = data_loaded.get('profiles', [])
            self.active_profile_id = data_loaded.get('active_profile_id', None)

            print(f"[KB Load] KnowledgeBase state loaded from {filename}")

        except FileNotFoundError:
            print(f"[KB Load Error] File not found: {filename}. Initializing with empty KB.")
            # Re-initialize to a clean state if file not found
            self.__init__() 
        except json.JSONDecodeError as e:
            print(f"[KB Load Error] Invalid JSON in file {filename}: {e}. KB might be partially loaded or empty.")
        except Exception as e:
            print(f"[KB Load Error] An unexpected error occurred: {e}. KB might be unstable.")

    def add_source(self, source_type: str, source_description: str): # Changed `source` to `source_description`
        if source_type.lower() == 'primary':
            self.primary_sources.append(source_description)
        elif source_type.lower() == 'secondary':
            self.secondary_sources.append(source_description)
        elif source_type.lower() == 'tertiary':
            self.tertiary_sources.append(source_description)
        else:
            raise ValueError("Invalid source_type. Must be 'primary', 'secondary', or 'tertiary'.")
        print(f"[KB Source] Added {source_type} source: {source_description}")

    # --- Generalized Data Fetching (using existing methods) ---
    def fetch_data(self, data_type: str, **kwargs) -> list:
        """
        Generalized method to fetch supported data types.
        Example: kb.fetch_data('statutes', jurisdiction='Tennessee', max_sections=5)
                 kb.fetch_data('cases', court_jurisdiction='Federal', max_pages_per_source=2)
                 kb.fetch_data('constitution', country='US')
        """
        data_type_lower = data_type.lower()
        print(f"[KB Fetch] Attempting to fetch data for type: '{data_type_lower}' with params: {kwargs}")

        if data_type_lower in ['statute', 'statutes']:
            jurisdiction = kwargs.get('jurisdiction', 'Tennessee') # Default if not provided
            if jurisdiction.lower() in ["tennessee", "tn"]:
                 max_items = kwargs.get('max_sections', kwargs.get('max_items', 10))
                 return self.fetch_tn_statutes_justia(max_sections=max_items)
            else:
                print(f"[KB Fetch Warning] Statute fetching for '{jurisdiction}' not specifically implemented beyond TN/Justia.")
                return []
        
        elif data_type_lower in ['case', 'cases', 'caselaw']:
            court_jurisdiction = kwargs.get('court_jurisdiction', kwargs.get('jurisdiction', 'Tennessee'))
            max_pages = kwargs.get('max_pages_per_source', kwargs.get('max_pages', 5))
            return self.fetch_case_law_data(court_jurisdiction=court_jurisdiction, max_pages_per_source=max_pages)

        elif data_type_lower in ['constitution']:
            # Country parameter is not directly used by fetch_us_constitution but good for extensibility
            # country = kwargs.get('country', 'US') 
            return self.fetch_us_constitution()
            
        else:
            print(f"[KB Fetch Error] Data type '{data_type}' not supported for direct fetching via this method.")
            # Consider raising ValueError or returning empty list based on desired strictness
            raise ValueError(f"Data type '{data_type}' not supported for fetching.")

    # --- Profile Management ---
    # These methods manage profiles in the in-memory list `self.profiles`.
    # The web app MVP would use its own DB-backed profile management if profiles were part of MVP.
    def _ensure_profiles_initialized(self):
        if not hasattr(self, 'profiles') or self.profiles is None: # Check for None as well
            self.profiles = []
        if not hasattr(self, 'active_profile_id'):
            self.active_profile_id = None
            
    def create_profile(self, profile_data: dict) -> dict:
        self._ensure_profiles_initialized()
        if 'name' not in profile_data or not profile_data['name']: # Ensure name is not empty
            raise ValueError("Profile must have a non-empty 'name'.")
        
        new_profile = profile_data.copy()
        new_profile['id'] = str(uuid.uuid4()) # Assign a new ID
        self.profiles.append(new_profile)
        print(f"[Profile] Created profile: {new_profile['name']} (ID: {new_profile['id']})")
        return new_profile

    def list_profiles(self) -> list:
        self._ensure_profiles_initialized()
        return list(self.profiles) # Return a copy

    def get_profile_by_id(self, profile_id: str) -> dict | None:
        self._ensure_profiles_initialized()
        for p in self.profiles:
            if p.get('id') == profile_id:
                return p
        return None

    def update_profile(self, profile_id: str, updates: dict) -> bool:
        self._ensure_profiles_initialized()
        profile_to_update = self.get_profile_by_id(profile_id)
        if profile_to_update:
            # Prevent 'id' from being updated
            if 'id' in updates:
                del updates['id']
            # Ensure name is not updated to empty if 'name' is in updates
            if 'name' in updates and not updates['name']:
                 raise ValueError("Profile name cannot be updated to empty.")
            
            profile_to_update.update(updates)
            print(f"[Profile] Updated profile ID: {profile_id}")
            return True
        print(f"[Profile Error] Update failed: Profile ID {profile_id} not found.")
        return False

    def delete_profile(self, profile_id: str) -> bool:
        self._ensure_profiles_initialized()
        original_len = len(self.profiles)
        self.profiles = [p for p in self.profiles if p.get('id') != profile_id]
        if len(self.profiles) < original_len:
            if self.active_profile_id == profile_id:
                self.active_profile_id = None # Clear active if deleted
                print(f"[Profile] Deleted active profile ID: {profile_id}. Active profile cleared.")
            else:
                print(f"[Profile] Deleted profile ID: {profile_id}")
            return True
        print(f"[Profile Error] Delete failed: Profile ID {profile_id} not found.")
        return False

    def set_active_profile(self, profile_id: str) -> bool:
        self._ensure_profiles_initialized()
        profile_to_set = self.get_profile_by_id(profile_id)
        if profile_to_set:
            self.active_profile_id = profile_id
            print(f"[Profile] Active profile set to: {profile_to_set['name']} (ID: {profile_id})")
            return True
        print(f"[Profile Error] Set active failed: Profile ID {profile_id} not found.")
        return False

    def get_active_profile(self) -> dict | None:
        self._ensure_profiles_initialized()
        if self.active_profile_id:
            return self.get_profile_by_id(self.active_profile_id)
        return None

    # --- CRUD for EthicalGuidelineRecord ---
    def validate_ethical_guideline_record(self, record: dict):
        if 'title' not in record or not record['title']:
            raise ValueError("EthicalGuidelineRecord must have a non-empty 'title'.")
        if 'principle' not in record or not record['principle']:
            raise ValueError("EthicalGuidelineRecord must have a 'principle'.")
        if 'source' not in record or not record['source']:
            raise ValueError("EthicalGuidelineRecord must have a 'source'.")
        # 'notes' and 'tags' are optional

    def create_ethical_guideline_record(self, record: dict) -> dict:
        self.validate_ethical_guideline_record(record)
        record = record.copy()
        record['id'] = str(uuid.uuid4())
        if not hasattr(self, 'ethical_guideline_records'):
            self.ethical_guideline_records = []
        self.ethical_guideline_records.append(record)
        # TODO: Audit log: EthicalGuidelineRecord created
        return record

    def list_ethical_guideline_records(self) -> list:
        if not hasattr(self, 'ethical_guideline_records'):
            self.ethical_guideline_records = []
        return list(self.ethical_guideline_records)

    def update_ethical_guideline_record(self, record_id: str, updates: dict) -> bool:
        if not hasattr(self, 'ethical_guideline_records'):
            self.ethical_guideline_records = []
        for r in self.ethical_guideline_records:
            if r.get('id') == record_id:
                self.validate_ethical_guideline_record({**r, **updates})
                r.update(updates)
                # TODO: Audit log: EthicalGuidelineRecord updated
                return True
        return False

    def delete_ethical_guideline_record(self, record_id: str) -> bool:
        if not hasattr(self, 'ethical_guideline_records'):
            self.ethical_guideline_records = []
        for i, r in enumerate(self.ethical_guideline_records):
            if r.get('id') == record_id:
                del self.ethical_guideline_records[i]
                # TODO: Audit log: EthicalGuidelineRecord deleted
                return True
        return False

    # --- Import Catholic teachings from JSON file ---
    def import_catholic_teachings(self, kb_path=None):
        """
        Import Catholic teachings from a JSON file and add as EthicalGuidelineRecords.
        Each entry should be a dict with at least: title, principle, source (notes/tags optional).
        """
        import json
        from .config import CATHOLIC_TEACHINGS_KB_PATH
        path = kb_path or CATHOLIC_TEACHINGS_KB_PATH
        try:
            with open(path, 'r', encoding='utf-8') as f:
                teachings = json.load(f)
            count = 0
            for entry in teachings:
                try:
                    self.create_ethical_guideline_record(entry)
                    count += 1
                except Exception as e:
                    print(f"[Import] Skipped entry due to error: {e}")
            print(f"[Import] Imported {count} Catholic teachings from {path}.")
            return count
        except Exception as e:
            print(f"[Import] Failed to import Catholic teachings: {e}")
            return 0

    def ingest_document(self, doc):
        self.create_document(doc)

    def preprocess(self):
        pass

    def fetch_caselaw_access_project(self, court: str = "tn", page_size: int = 20, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches opinions from the Caselaw Access Project API for a given court (default: Tennessee).
        Returns a list of opinions (dicts).
        """
        url = f"https://api.case.law/v1/cases/"
        params = {
            "court": court,
            "page_size": page_size,
            "page": 1 # Start with page 1
        }
        opinions = []
        current_page = 1
        while current_page <= max_pages:
            params["page"] = current_page
            try:
                resp = requests.get(url, params=params, timeout=10) # Added timeout
                resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                data = resp.json()
                opinions.extend(data.get("results", []))
                if not data.get("next"): # Check if there's a next page
                    break 
            except requests.exceptions.RequestException as e:
                print(f"[Error] Request to Caselaw Access Project failed: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"[Error] Could not parse JSON from Caselaw Access Project: {e}")
                print(f"Response content: {resp.text[:500] if resp else 'No response'}")
                break
            current_page +=1
        return opinions

    def fetch_courtlistener(self, jurisdiction: str = "tenn", page_size: int = 20, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches opinions from CourtListener API for a given jurisdiction (default: Tennessee).
        Returns a list of opinions (dicts).
        """
        url = "https://www.courtlistener.com/api/rest/v3/opinions/"
        params = {
            "jurisdiction": jurisdiction,
            "page_size": page_size,
            "page": 1 # Start with page 1
        }
        opinions = []
        current_page = 1
        while current_page <= max_pages:
            params["page"] = current_page
            try:
                resp = requests.get(url, params=params, timeout=10) # Added timeout
                resp.raise_for_status()
                data = resp.json()
                opinions.extend(data.get("results", []))
                if not data.get("next"): # Check if there's a next page
                    break
            except requests.exceptions.RequestException as e:
                print(f"[Error] Request to CourtListener failed: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"[Error] Could not parse JSON from CourtListener: {e}")
                print(f"Response content: {resp.text[:500] if resp else 'No response'}")
                break
            current_page += 1
        return opinions
        
    def save_to_gcloud(self, data: List[Dict[str, Any]], bucket_name: str, filename: str) -> bool:
        """
        Saves the given data to a Google Cloud Storage bucket as a JSON file.
        Requires the GOOGLE_APPLICATION_CREDENTIALS env variable to be set.
        """
        try:
            from google.cloud import storage # Import moved here
            import json # Import moved here
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(json.dumps(data), content_type='application/json')
            print(f"[GCloud] Successfully saved to {bucket_name}/{filename}")
            return True
        except ImportError:
            print("[GCloud Error] google-cloud-storage library not found. Please install it.")
            return False
        except Exception as e:
            print(f"[GCloud Error] {e}")
            return False

    def human_review(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Allows a human to review and approve/reject each item in the data list.
        Returns a list of approved items.
        """
        approved = []
        if not data: # Handle empty data
            return approved
            
        for item in data:
            print("\n--- Legal Document Preview ---")
            # Attempt to find a name or use a snippet
            preview_name = item.get("caseName") or item.get("case_name") or item.get("title")
            if preview_name:
                print(preview_name)
            else:
                print(str(item)[:500]) # Fallback to raw snippet
            print("-----------------------------")
            
            while True: # Loop for valid input
                resp = input("Approve this document? (y/n): ").strip().lower()
                if resp in ['y', 'n']:
                    break
                print("Invalid input. Please enter 'y' or 'n'.")

            if resp == 'y':
                approved.append(item)
        return approved

    def fetch_tn_statutes_justia(self, max_sections: int = 10) -> list:
        """
        Fetches Tennessee statutes from Justia (public domain, HTML scraping).
        Returns a list of statute dicts (section, title, text).
        Requires 'beautifulsoup4' (bs4) to be installed.
        """
        try:
            from bs4 import BeautifulSoup # Import moved here
        except ImportError:
            print("[Error] beautifulsoup4 is not installed. Please install with 'pip install beautifulsoup4'.")
            return []
        
        base_url = "https://law.justia.com/codes/tennessee/2021/title-39/" # Using 2021 as example
        statutes = []
        
        # Assuming sections are consecutively numbered chapters for this example
        # This part is highly dependent on Justia's URL structure for TN statutes
        # For Title 39, it seems to be chapter-based.
        # Example: https://law.justia.com/codes/tennessee/2021/title-39/chapter-11/
        # We'd need a way to discover valid chapter numbers or a different approach.
        # The original code iterates `section` from 1 to max_sections and appends to base_url
        # This might not align with how Justia structures its URLs for TN statutes (title/chapter/part/section)
        # For simplicity, I'll keep the loop but acknowledge it might need adjustment for real TN statutes.

        print(f"[Info] Attempting to fetch up to {max_sections} sections/chapters from {base_url}...")
        # This loop assumes 'section' maps to a chapter or a main page for that number in the URL.
        for section_num in range(1, max_sections + 1): 
            # This URL construction might need to be more specific (e.g., targeting chapters or specific sections)
            # For example, if 'section' refers to chapters:
            url = f"{base_url}chapter-{section_num}/" 
            # Or if it refers to a generic section index page (less likely for Justia's deep links)
            # url = f"{base_url}{section_num}/" # Original assumption

            print(f"[Info] Fetching {url}")
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Extracting title: Justia's structure can vary.
                # This is a generic attempt; specific selectors are usually needed.
                title_tag = soup.find('h1') or soup.find('h2') # Common title tags
                title = title_tag.text.strip() if title_tag else f"Tennessee Code - Title 39 - Chapter/Section {section_num}"
                
                # Extracting text: This is also generic.
                # Often, legal text is within specific divs or <p> tags with certain classes.
                text_content = []
                # Look for a main content area if possible
                main_content_div = soup.find('div', class_='law-text-content') # Example class
                if main_content_div:
                    paragraphs = main_content_div.find_all('p')
                else: # Fallback to all p tags if no specific content div
                    paragraphs = soup.find_all('p')

                for p in paragraphs:
                    text_content.append(p.get_text(separator='\n', strip=True))
                
                full_text = '\n'.join(text_content)

                if not full_text: # If no text found, maybe it was just a listing page
                    print(f"[Warning] No text content found for {url}. It might be an index page or the structure changed.")
                    continue

                statutes.append({"section_number": str(section_num), "title": title, "text": full_text, "source_url": url})
                if len(statutes) >= max_sections: # Control how many actual statutes are collected
                    break

            except requests.exceptions.RequestException as e:
                print(f"[Error] Could not fetch {url}: {e}")
                # Continue to next section if one fails, or break if too many failures
            except Exception as e:
                print(f"[Error] Error parsing {url}: {e}")
        
        print(f"[Info] Fetched {len(statutes)} statutes.")
        return statutes

    def fetch_us_constitution(self) -> list:
        """
        Fetches the U.S. Constitution from the National Archives website (amendments page).
        Returns a list of articles and amendments (title, text).
        """
        # URL for amendments 11-27
        url_amendments_11_27 = "https://www.archives.gov/founding-docs/amendments-11-27"
        # URL for Bill of Rights (Amendments 1-10)
        url_bill_of_rights = "https://www.archives.gov/founding-docs/bill-of-rights-transcript"
        # URL for the Constitution itself (Articles)
        url_articles = "https://www.archives.gov/founding-docs/constitution-transcript"

        constitution_parts = []
        
        try:
            from bs4 import BeautifulSoup # Import moved here
        except ImportError:
            print("[Error] beautifulsoup4 is not installed. Please install with 'pip install beautifulsoup4'.")
            return []

        sources_to_fetch = {
            "Articles": url_articles,
            "Bill of Rights": url_bill_of_rights,
            "Amendments 11-27": url_amendments_11_27,
        }

        for part_name, url in sources_to_fetch.items():
            print(f"[Info] Fetching {part_name} from {url}...")
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Scraping logic is highly dependent on the specific page structure of archives.gov
                # This needs to be robust and adaptable. The class 'field-item even' might not be universal.
                # For a more robust solution, one might need different selectors for articles vs. amendments.

                if "constitution-transcript" in url: # Articles
                    # Structure for articles is often different, e.g., `<h2>Article. I.</h2><p>Section. 1.</p>`
                    # This is a simplified example; actual parsing would be more complex.
                    article_elements = soup.select('h2, h3, p') # Basic tags for articles
                    current_title = part_name
                    current_text = []
                    for element in article_elements:
                        if element.name in ['h2', 'h3']: # New article or major section
                            if current_text: # Save previous article's text
                                constitution_parts.append({"title": current_title, "text": '\n'.join(current_text).strip(), "source": url})
                                current_text = []
                            current_title = element.get_text(strip=True)
                        elif element.name == 'p':
                            current_text.append(element.get_text(strip=True))
                    if current_text: # Append the last collected text
                         constitution_parts.append({"title": current_title, "text": '\n'.join(current_text).strip(), "source": url})


                else: # Amendments (Bill of Rights & 11-27)
                    # The original code used 'div.field-item.even', this might be specific to one page.
                    # Let's try a more general approach if that fails.
                    content_blocks = soup.find_all('div', class_='field--name-field-historical-description') # Common on archives.gov
                    if not content_blocks: # Fallback if the above class isn't found
                        content_blocks = soup.select('article p, article h3') # Generic content selectors

                    for block in content_blocks:
                        title_tag = block.find('h3') or block.find('h2') # Amendment titles often in h3
                        title = title_tag.get_text(strip=True) if title_tag else part_name # Fallback title

                        # Get all paragraphs within this block
                        text_elements = block.find_all('p')
                        text = '\n'.join([p.get_text(strip=True) for p in text_elements if p.get_text(strip=True)])
                        
                        if text: # Only add if text was found
                            constitution_parts.append({"title": title, "text": text, "source": url})
            
            except requests.exceptions.RequestException as e:
                print(f"[Error] Could not fetch {url}: {e}")
            except Exception as e:
                print(f"[Error] Error parsing {url}: {e}")

        print(f"[Info] Fetched {len(constitution_parts)} parts of the Constitution.")
        return constitution_parts

    def fetch_case_law_data(self, court_jurisdiction: str = "Tennessee", max_pages_per_source: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches case law data from various sources for a given court/jurisdiction.
        Returns a merged list of case law records.
        The 'court_jurisdiction' parameter should be mapped to specific API parameters.
        """
        all_data = []
        
        # Map general "Tennessee" to specific API params
        cap_court_param = "tn" # Default for Caselaw Access Project if 'Tennessee'
        cl_jurisdiction_param = "tenn" # Default for CourtListener if 'Tennessee'

        # Basic mapping (can be expanded)
        if court_jurisdiction.lower() == "federal":
            cap_court_param = "scotus" # Example: Supreme Court for CAP
            cl_jurisdiction_param = "us"   # Example: All federal for CourtListener
        # Add more sophisticated mapping if needed based on input `court_jurisdiction`

        print(f"[Info] Fetching from Caselaw Access Project for court param: '{cap_court_param}'...")
        cap_data = self.fetch_caselaw_access_project(court=cap_court_param, max_pages=max_pages_per_source)
        if cap_data:
            for item in cap_data: item['data_source'] = 'Caselaw Access Project' # Tag source
            all_data.extend(cap_data)
        print(f"[Info] Fetched {len(cap_data)} records from CAP.")

        print(f"[Info] Fetching from CourtListener for jurisdiction param: '{cl_jurisdiction_param}'...")
        cl_data = self.fetch_courtlistener(jurisdiction=cl_jurisdiction_param, max_pages=max_pages_per_source)
        if cl_data:
            for item in cl_data: item['data_source'] = 'CourtListener' # Tag source
            all_data.extend(cl_data)
        print(f"[Info] Fetched {len(cl_data)} records from CourtListener.")
        
        print(f"[Info] Total case law records fetched: {len(all_data)}.")
        return all_data

    def fetch_and_store_case_law(self, court_jurisdiction: str = "Tennessee", bucket_name: str = "your-bucket-name", max_pages_per_source: int = 5, auto_approve_review: bool = False):
        """
        Fetches case law data and stores it in a Google Cloud Storage bucket.
        """
        print(f"\n--- Starting Case Law Fetch & Store for: {court_jurisdiction} ---")
        data = self.fetch_case_law_data(court_jurisdiction=court_jurisdiction, max_pages_per_source=max_pages_per_source)
        if not data:
            print("[Warning] No case law data found to store.")
            return

        # Standardize filename based on jurisdiction
        filename_court_jurisdiction = court_jurisdiction.lower().replace(" ", "_")
        raw_filename = f"case_law/{filename_court_jurisdiction}/raw_data_{uuid.uuid4().hex[:8]}.json"
        approved_filename = f"case_law/{filename_court_jurisdiction}/approved_data_{uuid.uuid4().hex[:8]}.json"

        print(f"[Info] Saving raw data to GCS: {bucket_name}/{raw_filename}")
        if self.save_to_gcloud(data, bucket_name, raw_filename):
             print("[Info] Raw data saved successfully.")
        else:
            print("[Error] Failed to save raw data to GCS.")

        print("[Info] Starting human review process for fetched case law...")
        if auto_approve_review:
            print("[Info] Auto-approving all items for review (debug/testing mode).")
            approved_data = data # In auto-approve, all data is "approved"
        else:
            approved_data = self.human_review(data)
        
        if approved_data:
            print(f"[Info] {len(approved_data)} items approved. Saving approved data to GCS: {bucket_name}/{approved_filename}")
            if self.save_to_gcloud(approved_data, bucket_name, approved_filename):
                print("[Info] Approved data saved successfully.")
            else:
                print("[Error] Failed to save approved data to GCS.")
        else:
            print("[Info] No data was approved during human review.")
        print("--- Case Law Fetch & Store Completed ---")


    def fetch_statutes_and_store(self, jurisdiction: str = "Tennessee", max_items: int = 10, bucket_name: str = "your-bucket-name", auto_approve_review: bool = False):
        """
        Fetches statutes (e.g. TN from Justia) and stores them in GCS.
        'max_items' refers to max_sections for Justia TN.
        """
        print(f"\n--- Starting Statute Fetch & Store for: {jurisdiction} ---")
        statutes = []
        if jurisdiction.lower() in ["tennessee", "tn"]:
            print(f"[Info] Fetching Tennessee statutes from Justia (max_sections={max_items})...")
            statutes = self.fetch_tn_statutes_justia(max_sections=max_items)
        else:
            print(f"[Warning] Statute fetching for '{jurisdiction}' is not implemented beyond Tennessee/Justia in this version.")
            return

        if not statutes:
            print(f"[Warning] No statutes found for {jurisdiction} to store.")
            return

        filename_jurisdiction = jurisdiction.lower().replace(" ", "_")
        raw_filename = f"statutes/{filename_jurisdiction}/raw_data_{uuid.uuid4().hex[:8]}.json"
        approved_filename = f"statutes/{filename_jurisdiction}/approved_data_{uuid.uuid4().hex[:8]}.json"

        print(f"[Info] Saving raw statutes to GCS: {bucket_name}/{raw_filename}")
        if self.save_to_gcloud(statutes, bucket_name, raw_filename):
            print("[Info] Raw statutes saved successfully.")
        else:
            print("[Error] Failed to save raw statutes to GCS.")
        
        print("[Info] Starting human review process for fetched statutes...")
        if auto_approve_review:
            print("[Info] Auto-approving all items for review (debug/testing mode).")
            approved_statutes = statutes
        else:
            approved_statutes = self.human_review(statutes)

        if approved_statutes:
            print(f"[Info] {len(approved_statutes)} statutes approved. Saving to GCS: {bucket_name}/{approved_filename}")
            if self.save_to_gcloud(approved_statutes, bucket_name, approved_filename):
                print("[Info] Approved statutes saved successfully.")
            else:
                print("[Error] Failed to save approved statutes to GCS.")
        else:
            print("[Info] No statutes were approved during human review.")
        print("--- Statute Fetch & Store Completed ---")


    def run_pipeline(self, court_jurisdiction: str = "Tennessee", max_case_pages_per_source: int = 5, 
                     statute_jurisdiction: str = "Tennessee", max_statute_items: int = 10, 
                     bucket_name: str = "your-bucket-name", auto_approve_review: bool = False):
        """
        Runs the data fetching pipeline: fetches case law, fetches statutes, and stores both in Google Cloud Storage.
        """
        print("\n===== Starting Data Ingestion Pipeline =====")
        self.fetch_and_store_case_law(
            court_jurisdiction=court_jurisdiction, 
            bucket_name=bucket_name, 
            max_pages_per_source=max_case_pages_per_source,
            auto_approve_review=auto_approve_review
        )
        self.fetch_statutes_and_store(
            jurisdiction=statute_jurisdiction, 
            max_items=max_statute_items, 
            bucket_name=bucket_name,
            auto_approve_review=auto_approve_review
        )
        # Could add Constitution fetching here too if desired
        # print("[Info] Fetching US Constitution...")
        # constitution_data = self.fetch_us_constitution()
        # if constitution_data:
        #     self.save_to_gcloud(constitution_data, bucket_name, f"constitutions/us_constitution_{uuid.uuid4().hex[:8]}.json")
        # else:
        #     print("[Warning] No constitution data fetched.")
        print("===== Data Ingestion Pipeline Completed =====")


    def test_integration(self, bucket_name_to_use="kb-integration-test-bucket"):
        """
        Runs a full integration test: fetch case law, fetch statutes, and store in GCloud.
        Uses small limits for quick testing.
        """
        print("\n===== Starting Integration Test =====")
        # Note: For real tests, ensure the bucket_name_to_use exists and you have permissions.
        # Using auto_approve_review = True to avoid needing user input during automated tests.
        self.run_pipeline(
            court_jurisdiction="Tennessee", 
            max_case_pages_per_source=1, # Small number for testing
            statute_jurisdiction="Tennessee",
            max_statute_items=1, # Small number for testing
            bucket_name=bucket_name_to_use,
            auto_approve_review=True 
        )
        print("===== Integration Test Completed =====")
        print(f"IMPORTANT: Check bucket '{bucket_name_to_use}' for test artifacts and clean up if necessary.")


    # --- Debugging versions of fetch methods ---
    def debug_fetch_caselaw_access_project(self, court: str = "tn", page_size: int = 1, max_pages: int = 1): # smaller defaults for debug
        """ Debugging version: prints requests and responses from Caselaw Access Project. """
        url = f"https://api.case.law/v1/cases/"
        params = {"court": court, "page_size": page_size}
        opinions = []
        for page_num in range(1, max_pages + 1):
            params["page"] = page_num
            print(f"[DEBUG CAP] Requesting: {url} with params {params}")
            try:
                resp = requests.get(url, params=params, timeout=10)
                print(f"[DEBUG CAP] Response Status: {resp.status_code}")
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                print(f"[DEBUG CAP] Fetched {len(results)} records from page {page_num}.")
                # print(f"[DEBUG CAP] Sample record: {results[0] if results else 'No results'}")
                opinions.extend(results)
                if not data.get("next"):
                    print("[DEBUG CAP] No more pages.")
                    break
            except requests.exceptions.RequestException as e:
                print(f"[DEBUG CAP Error] Request failed: {e}")
                if resp: print(f"[DEBUG CAP Error] Response content: {resp.text[:500]}")
                break
            except json.JSONDecodeError as e:
                print(f"[DEBUG CAP Error] JSON Parse failed: {e}")
                print(f"[DEBUG CAP Error] Response content: {resp.text[:500]}")
                break
        return opinions

    def debug_fetch_courtlistener(self, jurisdiction: str = "tenn", page_size: int = 1, max_pages: int = 1): # smaller defaults
        """ Debugging version: prints requests and responses from CourtListener. """
        url = "https://www.courtlistener.com/api/rest/v3/opinions/"
        params = {"jurisdiction": jurisdiction, "page_size": page_size}
        opinions = []
        for page_num in range(1, max_pages + 1):
            params["page"] = page_num
            print(f"[DEBUG CL] Requesting: {url} with params {params}")
            try:
                resp = requests.get(url, params=params, timeout=10)
                print(f"[DEBUG CL] Response Status: {resp.status_code}")
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                print(f"[DEBUG CL] Fetched {len(results)} records from page {page_num}.")
                # print(f"[DEBUG CL] Sample record: {results[0] if results else 'No results'}")
                opinions.extend(results)
                if not data.get("next"):
                    print("[DEBUG CL] No more pages.")
                    break
            except requests.exceptions.RequestException as e:
                print(f"[DEBUG CL Error] Request failed: {e}")
                if resp: print(f"[DEBUG CL Error] Response content: {resp.text[:500]}")
                break
            except json.JSONDecodeError as e:
                print(f"[DEBUG CL Error] JSON Parse failed: {e}")
                print(f"[DEBUG CL Error] Response content: {resp.text[:500]}")
                break
        return opinions

    def debug_save_to_gcloud(self, data: List[Dict[str, Any]], bucket_name: str, filename: str):
        """ Debugging version: prints data and parameters before attempting to save to GCloud. """
        print(f"[DEBUG GCloud] Attempting to save {len(data)} records to bucket '{bucket_name}' as '{filename}'.")
        if data:
            print(f"[DEBUG GCloud] First item sample: {data[0]}")
        else:
            print("[DEBUG GCloud] No data to save.")
        # Actual save call
        self.save_to_gcloud(data, bucket_name, filename)

    def debug_human_review(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ Debugging version: auto-approves all items for human review. """
        print("[DEBUG Review] Starting debug human review (auto-approving all).")
        if not data: return []
        for item in data:
            preview_name = item.get("caseName") or item.get("case_name") or item.get("title", "Unknown Title")
            print(f"[DEBUG Review] Auto-approving: {preview_name[:100]}")
        print(f"[DEBUG Review] Auto-approved {len(data)} items.")
        return list(data) # Return a copy

    def run_debug_pipeline(self, court_jurisdiction: str = "Tennessee", max_case_pages_per_source: int = 1, 
                           statute_jurisdiction: str = "Tennessee", max_statute_items: int = 1, 
                           bucket_name: str = "your-debug-bucket"):
        """ Runs the pipeline in debug mode with verbose output and auto-approvals. """
        print("\n===== Starting Data Ingestion Pipeline (DEBUG MODE) =====")
        
        # Debug Case Law Fetch & Store
        print(f"\n--- Debug Case Law Fetch & Store for: {court_jurisdiction} ---")
        # Use debug fetch methods
        cap_court_param = "tn" if court_jurisdiction.lower() == "tennessee" else court_jurisdiction.lower()
        cl_jurisdiction_param = "tenn" if court_jurisdiction.lower() == "tennessee" else court_jurisdiction.lower()

        print(f"[DEBUG Pipeline] Fetching from Caselaw Access Project (court: {cap_court_param})...")
        cap_data = self.debug_fetch_caselaw_access_project(court=cap_court_param, max_pages=max_case_pages_per_source)
        print(f"[DEBUG Pipeline] Fetching from CourtListener (jurisdiction: {cl_jurisdiction_param})...")
        cl_data = self.debug_fetch_courtlistener(jurisdiction=cl_jurisdiction_param, max_pages=max_case_pages_per_source)
        
        all_case_data = []
        if cap_data: all_case_data.extend(cap_data)
        if cl_data: all_case_data.extend(cl_data)

        if not all_case_data:
            print("[DEBUG Pipeline Warning] No case law data found.")
        else:
            filename_court = court_jurisdiction.lower().replace(" ", "_")
            raw_fn = f"case_law/{filename_court}/DEBUG_raw_data_{uuid.uuid4().hex[:8]}.json"
            approved_fn = f"case_law/{filename_court}/DEBUG_approved_data_{uuid.uuid4().hex[:8]}.json"
            self.debug_save_to_gcloud(all_case_data, bucket_name, raw_fn)
            approved_case_data = self.debug_human_review(all_case_data)
            if approved_case_data:
                self.debug_save_to_gcloud(approved_case_data, bucket_name, approved_fn)
        print("--- Debug Case Law Fetch & Store Completed ---")

        # Debug Statute Fetch & Store
        print(f"\n--- Debug Statute Fetch & Store for: {statute_jurisdiction} ---")
        statutes = []
        if statute_jurisdiction.lower() in ["tennessee", "tn"]:
            print(f"[DEBUG Pipeline] Fetching TN statutes from Justia (max_sections={max_statute_items})...")
            # Assuming fetch_tn_statutes_justia also has sufficient internal logging or can be wrapped.
            statutes = self.fetch_tn_statutes_justia(max_sections=max_statute_items) 
        else:
            print(f"[DEBUG Pipeline Warning] Statute fetching for '{statute_jurisdiction}' not implemented beyond TN.")

        if not statutes:
            print(f"[DEBUG Pipeline Warning] No statutes found for {statute_jurisdiction}.")
        else:
            filename_statute = statute_jurisdiction.lower().replace(" ", "_")
            raw_fn_stat = f"statutes/{filename_statute}/DEBUG_raw_data_{uuid.uuid4().hex[:8]}.json"
            approved_fn_stat = f"statutes/{filename_statute}/DEBUG_approved_data_{uuid.uuid4().hex[:8]}.json"
            self.debug_save_to_gcloud(statutes, bucket_name, raw_fn_stat)
            approved_statutes = self.debug_human_review(statutes)
            if approved_statutes:
                self.debug_save_to_gcloud(approved_statutes, bucket_name, approved_fn_stat)
        print("--- Debug Statute Fetch & Store Completed ---")
        
        print("===== Data Ingestion Pipeline (DEBUG MODE) Completed =====")
        print(f"IMPORTANT: Check bucket '{bucket_name}' for DEBUG test artifacts and clean up if necessary.")