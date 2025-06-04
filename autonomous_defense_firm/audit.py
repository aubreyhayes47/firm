"""
Audit logging utility for Law by Keystone, with ethical event support.
"""
import logging
from datetime import datetime
from .config import LOG_FILE, LOG_LEVEL

logger = logging.getLogger("law_by_keystone_audit")
logger.setLevel(LOG_LEVEL)
if not logger.handlers:
    fh = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def log_audit_event(event_type: str, user: str = None, details: dict = None):
    msg = f"[AUDIT] {event_type}"
    if user:
        msg += f" | user={user}"
    if details:
        msg += f" | details={details}"
    logger.info(msg)

# Example usage:
# log_audit_event("ETHICAL_MODE_CHANGE", user="admin", details={"from": "standard", "to": "catholic_teachings_aligned"})
# log_audit_event("SENSITIVE_DATA_ACCESS", user="attorney1", details={"case_id": "123", "action": "view"})
