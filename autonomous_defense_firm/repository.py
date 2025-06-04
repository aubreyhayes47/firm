"""
Repository and service layer for Law by Keystone, supporting ethical querying.
"""
from typing import List, Dict, Any, Optional
from .knowledge_base import KnowledgeBase

class BaseRepository:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

class CaseRepository(BaseRepository):
    def get_cases(self, ethical_tag: Optional[str] = None, guideline_id: Optional[str] = None) -> List[Dict]:
        cases = self.kb.list_cases()
        if ethical_tag:
            cases = [c for c in cases if ethical_tag in c.get('ethical_tags', [])]
        if guideline_id:
            cases = [c for c in cases if guideline_id in c.get('ethical_guideline_ids', [])]
        return cases

    def add_case(self, case: dict, ethical_tags=None, ethical_guideline_ids=None):
        return self.kb.create_case(case, ethical_tags=ethical_tags, ethical_guideline_ids=ethical_guideline_ids)

class DocumentRepository(BaseRepository):
    def get_documents(self, ethical_tag: Optional[str] = None, guideline_id: Optional[str] = None) -> List[Dict]:
        docs = self.kb.list_documents()
        if ethical_tag:
            docs = [d for d in docs if ethical_tag in d.get('ethical_tags', [])]
        if guideline_id:
            docs = [d for d in docs if guideline_id in d.get('ethical_guideline_ids', [])]
        return docs

    def add_document(self, doc: dict, ethical_tags=None, ethical_guideline_ids=None):
        return self.kb.create_document(doc, ethical_tags=ethical_tags, ethical_guideline_ids=ethical_guideline_ids)

# Additional repositories (StatuteRepository, ContractRepository, etc.) can be added similarly.
