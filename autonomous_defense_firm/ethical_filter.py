"""
Ethical Filter for Law by Keystone: Ensures compliance with ABA/State Bar model rules.
Checks data/actions for ethical issues before allowing them to proceed.
"""
import re
from typing import Any, Dict, Tuple

# Example: Key rules to check (expand as needed)
ABA_RULES = {
    'confidentiality': {
        'rule': 'ABA Model Rule 1.6',
        'desc': 'A lawyer shall not reveal information relating to the representation of a client unless the client gives informed consent.'
    },
    'conflict_of_interest': {
        'rule': 'ABA Model Rule 1.7',
        'desc': 'A lawyer shall not represent a client if the representation involves a concurrent conflict of interest.'
    },
    'unauthorized_practice': {
        'rule': 'ABA Model Rule 5.5',
        'desc': 'A lawyer shall not practice law in a jurisdiction in violation of the regulation of the legal profession in that jurisdiction.'
    },
    # Add more rules as needed
}

def check_confidentiality(data: Any) -> Tuple[str, str]:
    # Simple PII/PHI regex check (expand for real use)
    patterns = [r'\bSSN\b', r'\bSocial Security\b', r'\bDOB\b', r'\bDate of Birth\b', r'\bmedical\b', r'\bdiagnosis\b']
    text = str(data)
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return ('warn', f"Potential confidential info detected: '{pat}'. See {ABA_RULES['confidentiality']['rule']}")
    return ('pass', '')

def check_conflict_of_interest(data: Any, context: Dict) -> Tuple[str, str]:
    # Example: Check if client name matches existing adverse party (stub)
    client = data.get('client') if isinstance(data, dict) else None
    adverse_parties = context.get('adverse_parties', [])
    if client and client in adverse_parties:
        return ('block', f"Conflict of interest: client '{client}' is an adverse party. See {ABA_RULES['conflict_of_interest']['rule']}")
    return ('pass', '')

def check_unauthorized_practice(user: Dict, context: Dict) -> Tuple[str, str]:
    # Example: Check if user is authorized for jurisdiction (stub)
    jurisdiction = context.get('jurisdiction')
    authorized = user.get('jurisdictions', []) if user else []
    if jurisdiction and jurisdiction not in authorized:
        return ('block', f"Unauthorized practice in {jurisdiction}. See {ABA_RULES['unauthorized_practice']['rule']}")
    return ('pass', '')

def check_ethics(data: Any, action_type: str, user: Dict = None, context: Dict = None) -> Dict:
    """
    Main entry: Checks data/action for ethical compliance.
    Returns dict: {'result': 'pass'|'warn'|'block', 'explanation': str, 'rule': str}
    """
    context = context or {}
    # Run all relevant checks
    checks = []
    # Confidentiality check for all data
    res, expl = check_confidentiality(data)
    if res != 'pass':
        checks.append({'result': res, 'explanation': expl, 'rule': ABA_RULES['confidentiality']['rule']})
    # Conflict check for client-related actions
    if action_type in ('create_client', 'update_client', 'create_case', 'update_case'):
        res, expl = check_conflict_of_interest(data, context)
        if res != 'pass':
            checks.append({'result': res, 'explanation': expl, 'rule': ABA_RULES['conflict_of_interest']['rule']})
    # Unauthorized practice check for legal actions
    if action_type in ('create_case', 'update_case', 'legal_action'):
        res, expl = check_unauthorized_practice(user, context)
        if res != 'pass':
            checks.append({'result': res, 'explanation': expl, 'rule': ABA_RULES['unauthorized_practice']['rule']})
    # Return the most severe result
    if any(c['result'] == 'block' for c in checks):
        c = next(c for c in checks if c['result'] == 'block')
        return c
    if any(c['result'] == 'warn' for c in checks):
        c = next(c for c in checks if c['result'] == 'warn')
        return c
    return {'result': 'pass', 'explanation': '', 'rule': ''}
