"""
Module for legal data sourcing, acquisition, preprocessing, and structuring.
"""

import requests
import os
from typing import List, Dict, Any

class KnowledgeBase:
    def __init__(self):
        self.primary_sources = []
        self.secondary_sources = []
        self.tertiary_sources = []
        self.documents = []

    def add_source(self, source_type, source):
        if source_type == 'primary':
            self.primary_sources.append(source)
        elif source_type == 'secondary':
            self.secondary_sources.append(source)
        elif source_type == 'tertiary':
            self.tertiary_sources.append(source)

    def ingest_document(self, doc):
        self.documents.append(doc)

    def preprocess(self):
        # Placeholder for cleaning, standardizing, parsing, and tagging
        pass

    def fetch_caselaw_access_project(self, court: str = "tn", page_size: int = 20, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches opinions from the Caselaw Access Project API for a given court (default: Tennessee).
        Returns a list of opinions (dicts).
        """
        url = f"https://api.case.law/v1/cases/"
        params = {
            "court": court,
            "page_size": page_size
        }
        opinions = []
        for page in range(1, max_pages + 1):
            params["page"] = page
            resp = requests.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                opinions.extend(data.get("results", []))
                if not data.get("next"):
                    break
            else:
                break
        return opinions

    def fetch_courtlistener(self, jurisdiction: str = "tenn", page_size: int = 20, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches opinions from CourtListener API for a given jurisdiction (default: Tennessee).
        Returns a list of opinions (dicts).
        """
        url = "https://www.courtlistener.com/api/rest/v3/opinions/"
        params = {
            "jurisdiction": jurisdiction,
            "page_size": page_size
        }
        opinions = []
        for page in range(1, max_pages + 1):
            params["page"] = page
            resp = requests.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                opinions.extend(data.get("results", []))
                if not data.get("next"):
                    break
            else:
                break
        return opinions

    def save_to_gcloud(self, data: List[Dict[str, Any]], bucket_name: str, filename: str) -> bool:
        """
        Saves the given data to a Google Cloud Storage bucket as a JSON file.
        Requires the GOOGLE_APPLICATION_CREDENTIALS env variable to be set.
        """
        try:
            from google.cloud import storage
            import json
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(json.dumps(data), content_type='application/json')
            return True
        except Exception as e:
            print(f"[GCloud Error] {e}")
            return False

    def human_review(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Allows a human to review and approve/reject each item in the data list.
        Returns a list of approved items.
        """
        approved = []
        for item in data:
            print("\n--- Legal Document Preview ---")
            print(item.get("caseName") or item.get("case_name") or str(item)[:500])
            print("-----------------------------")
            resp = input("Approve this document? (y/n): ").strip().lower()
            if resp == 'y':
                approved.append(item)
        return approved

    def fetch_tn_statutes_justia(self, max_sections: int = 10) -> list:
        """
        Fetches Tennessee statutes from Justia (public domain, HTML scraping).
        Returns a list of statute dicts (section, title, text).
        """
        from bs4 import BeautifulSoup
        base_url = "https://law.justia.com/codes/tennessee/2021/title-39/"
        statutes = []
        for section in range(1, max_sections + 1):
            url = f"{base_url}{section}/"
            resp = requests.get(url)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.find('h1').text if soup.find('h1') else f"Section {section}"
            text = '\n'.join([p.text for p in soup.find_all('p')])
            statutes.append({"section": section, "title": title, "text": text})
        return statutes

    def fetch_us_constitution(self) -> list:
        """
        Fetches the U.S. Constitution from a public domain source (e.g., https://constitutioncenter.org/media/files/constitution.txt)
        Returns a list with a single dict.
        """
        url = "https://constitutioncenter.org/media/files/constitution.txt"
        resp = requests.get(url)
        if resp.status_code == 200:
            return [{"title": "U.S. Constitution", "text": resp.text}]
        return []

    def fetch_tn_constitution(self) -> list:
        """
        Fetches the Tennessee Constitution from a public domain source (HTML scraping).
        Returns a list with a single dict.
        """
        url = "https://www.capitol.tn.gov/about/docs/tn-constitution.pdf"
        # For demo, just store the link; PDF parsing can be added later
        return [{"title": "Tennessee Constitution", "url": url}]

    def fetch_oyez_supreme_court_cases(self, max_cases: int = 10) -> list:
        """
        Fetches recent U.S. Supreme Court cases from Oyez API.
        Returns a list of case dicts.
        """
        url = "https://api.oyez.org/cases"
        resp = requests.get(url)
        cases = []
        if resp.status_code == 200:
            data = resp.json()
            for case in data[:max_cases]:
                cases.append({"name": case.get("name"), "docket_number": case.get("docket_number"), "url": case.get("href")})
        return cases
