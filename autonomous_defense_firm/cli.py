"""
CLI entry point for the autonomous_defense_firm package.
Practice-area-neutral version: supports all law firm data types.
"""
import argparse
from autonomous_defense_firm.knowledge_base import KnowledgeBase
from autonomous_defense_firm.training import TrainingManager
from autonomous_defense_firm.audit import log_audit_event
# import sys # Not strictly needed for this version of cli.py
import uuid # For generating IDs if needed, though kb handles it internally
import logging
import json # For pretty printing dicts
import os # For file path operations
import getpass # For secure password input
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', # Added logger name
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__) # For CLI specific logs
kb_logger = logging.getLogger('KnowledgeBase') # If KB had its own logger
tm_logger = logging.getLogger('TrainingManager') # If TM had its own logger


def print_colored(text, color=None):
    """Print text with optional ANSI color (if supported)."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'end': '\033[0m',
    }
    if color and sys.stdout.isatty():
        print(f"{colors.get(color, '')}{text}{colors['end']}")
    else:
        print(text)


def print_help():
    # Enhanced help message with Discernment Mode and accessibility notes
    print("""
=================================
Autonomous Law Firm CLI - Help
=================================
Welcome! This CLI allows you to manage various data types for a law firm,
including clients, cases, legal documents, LLMs, profiles, and more.

Core Operations:
  - For most data types, you can: List, Add, Update, or Delete records.
  - Use the numbered menus to navigate.
  - When adding or updating, data is usually entered as key=value pairs,
    separated by commas (e.g., name=John Doe,contact=john@example.com).

Special Menus:
  - Training & Feedback: Manage training data, train models, evaluate.
  - LLM Management: Configure and manage Large Language Models.
  - Profile Management: Handle practice area/jurisdiction profiles.
  - Data Fetching: Retrieve external data like statutes or case law.

Discernment Mode:
  - When enabled, you will be prompted to pause and reflect before any critical or destructive action (delete, update, feedback, etc.).
  - Prompts include Catholic ethical reflection tips for clarity and prudence.
  - Toggle Discernment Mode from the main or profile menu.

Accessibility:
  - Warnings and errors are shown in color if your terminal supports it.
  - All actions are logged for traceability.

Backup & Restore:
  - Save all current data to a JSON file (e.g., backup.json).
  - Load data from a previously saved JSON file.

Tips:
  - Search/Filter: When listing items, you can often filter by keyword.
  - IDs: Most items are assigned a unique ID upon creation. Use these IDs
    for updating or deleting specific records.
  - For detailed field names required for each data type, refer to the
    'Add' option prompts or documentation.

Global Options (in menus):
  '0' or 'b': Go back to the previous menu.
  'q' or 'exit': Exit the CLI (usually from the main menu).
""")


def get_dict_from_input(prompt="Enter data as key=value pairs (comma separated):") -> dict:
    """Helper to get a dictionary from comma-separated key=value string."""
    print(prompt)
    raw = input("> ").strip()
    data = {}
    if not raw:
        return data
    for pair in raw.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            data[k.strip()] = v.strip()
        else:
            print_colored(f"Warning: Skipping malformed pair '{pair}'. Expected key=value format.", color='yellow')
    return data


def training_menu(tm, kb, discernment_state=None): # kb added for feedback linkage
    from autonomous_defense_firm.ethical_filter import check_ethics
    while True:
        print("\n--- Training & Feedback Menu ---")
        print("1. Submit Feedback (Ethical)")
        print("2. List Feedback")
        print("0. Back")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            feedback = input("Enter your feedback (ethical/legal focus encouraged): ")
            # --- Ethical Filter integration ---
            user = None
            try:
                user = getattr(globals().get('session', None), 'current_user', None)
            except Exception:
                user = None
            result = check_ethics(feedback, action_type='submit_feedback', user=user)
            if result['result'] == 'block':
                print_colored(f"[ETHICAL BLOCK] {result['explanation']}", color='red')
                log_audit_event("ETHICAL_BLOCK", user=user.get('username') if user else None, details=result)
                continue
            elif result['result'] == 'warn':
                print_colored(f"[ETHICAL WARNING] {result['explanation']}", color='yellow')
                override = input("Proceed anyway? (y/n): ").strip().lower()
                if override != 'y':
                    print("Feedback submission cancelled due to ethical warning.")
                    log_audit_event("ETHICAL_WARN_CANCEL", user=user.get('username') if user else None, details=result)
                    continue
                log_audit_event("ETHICAL_WARN_OVERRIDE", user=user.get('username') if user else None, details=result)
            # --- End Ethical Filter integration ---
            if discernment_state and not discernment_state.prompt("submit this feedback", tips=True):
                print("Feedback submission cancelled.")
                continue
            try:
                tm.submit_feedback(feedback)
                print("Feedback submitted. Thank you for your ethical contribution.")
            except Exception as e:
                print_colored(f"Error: {e}", color='red')
        elif choice == "2":
            feedbacks = tm.list_feedback()
            print(json.dumps(feedbacks, indent=2))
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def llm_menu(kb: KnowledgeBase, discernment_state=None):
    while True:
        print("\n--- LLM Management Menu ---")
        print("1. List LLMs")
        print("2. Add LLM")
        print("3. Update LLM")
        print("4. Delete LLM")
        print("5. Set Default LLM")
        print("6. Show Default LLM")
        print("7. Configure LLM API Key/Endpoint")
        print("0. Back to Main Menu")
        
        sub_choice = input("Choose an action (LLM Management): ").strip().lower()

        if sub_choice == "1":
            llms = kb.list_llms()
            if llms:
                print("\nAvailable LLM Configurations:")
                for idx, llm_conf in enumerate(llms):
                    default_marker = "(Default)" if llm_conf.get('is_default') else ""
                    print(f"  {idx+1}. ID: {llm_conf.get('id')}")
                    print(f"     Name: {llm_conf.get('name')} {default_marker}")
                    print(f"     Type: {llm_conf.get('type')}")
                    if llm_conf.get('type') == 'local':
                        print(f"     Path: {llm_conf.get('model_path', 'N/A')}")
                    elif llm_conf.get('type') == 'api':
                        print(f"     URL: {llm_conf.get('api_url', 'N/A')}")
                        print(f"     API Key: {'********' if llm_conf.get('api_key') else 'Not Set'}")
                    print("-" * 20)
            else:
                print("No LLM configurations found.")
        
        elif sub_choice == "2":
            name = input("Enter LLM name: ").strip()
            print("Select LLM type:")
            print("  1. Local (GGUF, llama.cpp, etc.)")
            print("  2. OpenAI API")
            print("  3. Anthropic API")
            print("  4. HuggingFace Inference API")
            print("  5. Custom API")
            llm_type_choice = input("Enter type number: ").strip()
            llm_type_map = {
                '1': 'local',
                '2': 'openai',
                '3': 'anthropic',
                '4': 'huggingface',
                '5': 'custom',
            }
            llm_type = llm_type_map.get(llm_type_choice)
            if not llm_type:
                print("Invalid LLM type selection.")
                continue
            llm_data = {'name': name, 'type': llm_type}
            if llm_type == 'local':
                llm_data['model_path'] = input("Enter local model path: ").strip()
            elif llm_type == 'openai':
                llm_data['api_url'] = input("Enter OpenAI API URL (default https://api.openai.com/v1): ").strip() or "https://api.openai.com/v1"
                llm_data['api_key'] = input("Enter OpenAI API key: ").strip()
                llm_data['model'] = input("Enter OpenAI model name (e.g., gpt-4): ").strip()
            elif llm_type == 'anthropic':
                llm_data['api_url'] = input("Enter Anthropic API URL (default https://api.anthropic.com/v1): ").strip() or "https://api.anthropic.com/v1"
                llm_data['api_key'] = input("Enter Anthropic API key: ").strip()
                llm_data['model'] = input("Enter Anthropic model name (e.g., claude-3-opus): ").strip()
            elif llm_type == 'huggingface':
                llm_data['api_url'] = input("Enter HuggingFace Inference API URL (default https://api-inference.huggingface.co/models): ").strip() or "https://api-inference.huggingface.co/models"
                llm_data['api_key'] = input("Enter HuggingFace API key: ").strip()
                llm_data['model'] = input("Enter HuggingFace model name (e.g., meta-llama/Llama-2-7b-chat-hf): ").strip()
            elif llm_type == 'custom':
                llm_data['api_url'] = input("Enter Custom API URL: ").strip()
                llm_data['api_key'] = input("Enter API key (if required): ").strip()
                llm_data['model'] = input("Enter model name (if required): ").strip()
            is_default_input = input("Set as default LLM? (y/n): ").strip().lower()
            is_default = is_default_input == 'y'
            llm_data['is_default'] = is_default
            try:
                created_llm = kb.create_llm(llm_data)
                if is_default and created_llm.get('id'):
                    kb.set_default_llm(created_llm['id'])
                print(f"LLM '{name}' added with ID '{created_llm.get('id')}'.")
                logger.info(f"LLM added: {created_llm}")
            except ValueError as ve:
                print_colored(f"Error adding LLM: {ve}", color='red')
            except Exception as e:
                print_colored(f"An unexpected error occurred: {e}", color='red')
                logger.error(f"Error adding LLM: {e}")

        elif sub_choice == "3":
            llm_id = input("Enter ID of LLM to update: ").strip()
            if not kb.get_profile_by_id(llm_id):
                llm_exists = any(l.get('id') == llm_id for l in kb.list_llms())
                if not llm_exists:
                    print(f"LLM with ID '{llm_id}' not found.")
                    continue
            print("Enter updates as key=value pairs (e.g., name=NewName,model_path=/new/path). Blank to skip.")
            updates = get_dict_from_input()
            if 'is_default' in updates:
                updates['is_default'] = updates['is_default'].lower() in ['true', 'y', 'yes', '1']
            if not updates:
                print("No updates provided.")
                continue
            try:
                if kb.update_llm(llm_id, updates):
                    print(f"LLM '{llm_id}' updated successfully.")
                    logger.info(f"LLM '{llm_id}' updated with {updates}")
                else:
                    print(f"Failed to update LLM '{llm_id}'. Not found.")
            except ValueError as ve:
                print_colored(f"Error updating LLM: {ve}", color='red')
            except Exception as e:
                print_colored(f"An unexpected error occurred during update: {e}", color='red')
                logger.error(f"Error updating LLM '{llm_id}': {e}")
        
        elif sub_choice == "4":
            llm_id = input("Enter ID of LLM to delete: ").strip()
            if discernment_state and not discernment_state.prompt("delete this LLM"):
                print("Action cancelled.")
                continue
            try:
                if kb.delete_llm(llm_id):
                    print(f"LLM '{llm_id}' deleted successfully.")
                    logger.info(f"LLM '{llm_id}' deleted")
                else:
                    print(f"LLM with ID '{llm_id}' not found.")
            except Exception as e:
                print_colored(f"An unexpected error occurred: {e}", color='red')
                logger.error(f"Error deleting LLM '{llm_id}': {e}")

        elif sub_choice == "5":
            llm_id = input("Enter ID of LLM to set as default: ").strip()
            try:
                if kb.set_default_llm(llm_id):
                    print(f"LLM '{llm_id}' is now the default.")
                    logger.info(f"LLM '{llm_id}' set as default.")
                else:
                    print(f"LLM with ID '{llm_id}' not found or failed to set as default.")
            except Exception as e:
                print_colored(f"An unexpected error occurred: {e}", color='red')
                logger.error(f"Error setting default LLM to '{llm_id}': {e}")
        elif sub_choice == "6":
            default_llm = kb.get_default_llm()
            if default_llm:
                print("Default LLM:")
                print(f"  ID: {default_llm.get('id')}")
                print(f"  Name: {default_llm.get('name')}")
                print(f"  Type: {default_llm.get('type')}")
                if default_llm.get('type') == 'local':
                    print(f"  Path: {default_llm.get('model_path', 'N/A')}")
                elif default_llm.get('type') == 'api':
                    print(f"  URL: {default_llm.get('api_url', 'N/A')}")
            else:
                print("No default LLM is currently set.")
        
        elif sub_choice == "7":
            llms = kb.list_llms()
            if not llms:
                print("No LLMs configured.")
                continue
            print("Select LLM to configure:")
            for idx, llm in enumerate(llms, 1):
                print(f"{idx}. {llm.get('name')} (ID: {llm.get('id')}) [{llm.get('type')}]" )
            llm_idx = input("Enter number of LLM to configure: ").strip()
            try:
                llm_idx = int(llm_idx) - 1
                if llm_idx < 0 or llm_idx >= len(llms):
                    print("Invalid selection.")
                    continue
                llm = llms[llm_idx]
            except Exception:
                print("Invalid input.")
                continue
            updates = {}
            if llm.get('type') == 'api' or llm.get('type') in ('openai', 'anthropic', 'huggingface', 'custom'):
                new_api_key = input(f"Enter new API key (leave blank to keep current): ").strip()
                if new_api_key:
                    updates['api_key'] = new_api_key
                new_api_url = input(f"Enter new API URL (leave blank to keep current): ").strip()
                if new_api_url:
                    updates['api_url'] = new_api_url
                new_model = input(f"Enter new model name (leave blank to keep current): ").strip()
                if new_model:
                    updates['model'] = new_model
            elif llm.get('type') == 'local':
                new_path = input(f"Enter new local model path (leave blank to keep current): ").strip()
                if new_path:
                    updates['model_path'] = new_path
            else:
                print("Unknown LLM type; cannot configure.")
                continue
            if not updates:
                print("No changes provided.")
                continue
            try:
                if kb.update_llm(llm.get('id'), updates):
                    print("LLM configuration updated.")
                    logger.info(f"LLM '{llm.get('id')}' configuration updated: {updates}")
                else:
                    print("Failed to update LLM configuration.")
            except Exception as e:
                print_colored(f"Error updating LLM configuration: {e}", color='red')
        elif sub_choice == "0" or sub_choice == "b":
            break
        else:
            print("Invalid choice in LLM Menu. Please try again.")


def profile_menu(kb, discernment_state=None):
    kb._ensure_profiles_initialized() # Ensure profile attributes exist

    while True:
        print("\n--- Profile Management Menu ---")
        print("1. View Profile")
        print("2. Edit Profile")
        print("3. Toggle Discernment Mode")
        print("0. Back")
        
        choice = input("Choose an option: ").strip()
        if choice == "1":
            profile = kb.get_profile()
            print(json.dumps(profile, indent=2))
        elif choice == "2":
            updates = get_dict_from_input(prompt="Enter updates as key=value pairs:")
            if discernment_state and not discernment_state.prompt("update your profile"): 
                print("Action cancelled.")
                continue
            try:
                if kb.update_profile(updates):
                    print("Profile updated.")
                else:
                    print("Profile update failed.")
            except Exception as e:
                print_colored(f"Error: {e}", color='red')
        elif choice == "3":
            if discernment_state:
                discernment_state.toggle()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def data_fetch_menu(kb, discernment_state=None):
    while True:
        print("\n--- Data Fetching Menu ---")
        print("1. Import Catholic/Ethical Source")
        print("2. List Imported Sources")
        print("0. Back")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            source = input("Enter source name or URL: ")
            if discernment_state and not discernment_state.prompt("import this source"): 
                print("Action cancelled.")
                continue
            try:
                kb.import_catholic_teaching(source)
                print("Source imported.")
            except Exception as e:
                print_colored(f"Error: {e}", color='red')
        elif choice == "2":
            sources = kb.list_imported_sources()
            print(json.dumps(sources, indent=2))
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def user_management_menu(kb, discernment_state=None):
    """CLI menu for user CRUD and authentication."""
    while True:
        print("\n--- User Management Menu ---")
        print("1. Create User")
        print("2. List Users")
        print("3. Update User")
        print("4. Delete User")
        print("5. Authenticate (Login Test)")
        print("0. Back to Main Menu")
        choice = input("Select option: ").strip()
        if choice == "1":
            username = input("Username: ").strip()
            role = input("Role (admin/lawyer/staff/client): ").strip()
            password = getpass.getpass("Password: ")
            try:
                user = kb.create_user({'username': username, 'role': role}, password)
                print(f"User '{username}' created with ID {user['id']}.")
            except Exception as e:
                print_colored(f"Error: {e}", color='red')
        elif choice == "2":
            users = kb.list_users()
            for u in users:
                print(f"ID: {u['id']} | Username: {u['username']} | Role: {u['role']}")
        elif choice == "3":
            user_id = input("User ID to update: ").strip()
            updates = {}
            if input("Update role? (y/n): ").strip().lower() == 'y':
                updates['role'] = input("New role: ").strip()
            if input("Update password? (y/n): ").strip().lower() == 'y':
                password = getpass.getpass("New password: ")
                user = next((u for u in kb.list_users() if u['id'] == user_id), None)
                if user:
                    user['password_hash'] = kb._hash_password(password)
            if updates:
                if kb.update_user(user_id, updates):
                    print("User updated.")
                else:
                    print("User not found or update failed.")
        elif choice == "4":
            user_id = input("User ID to delete: ").strip()
            if discernment_state and not discernment_state.prompt("delete this user"): 
                print("Action cancelled.")
                continue
            try:
                if kb.delete_user(user_id):
                    print("User deleted.")
                else:
                    print("User not found.")
            except Exception as e:
                print_colored(f"Error: {e}", color='red')
        elif choice == "5":
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")
            user = kb.authenticate_user(username, password)
            if user:
                print(f"Authenticated as {user['username']} (role: {user['role']})")
            else:
                print("Authentication failed.")
        elif choice == "0":
            break
        else:
            print("Invalid option.")


def user_guide(): # Simple user guide from original cli.py
    print("""
Welcome to the Autonomous Law Firm CLI Interactive User Guide!
-------------------------------------------------------------
This guide will walk you through the main features of the system step by step.

Catholic Discernment Tips:
- Before major actions, pause and reflect: Does this serve truth, justice, and the dignity of all involved?
- Seek prayerful discernment and counsel for difficult or ethically ambiguous decisions.
- Remember the preferential option for the vulnerable and the common good.
- Use Discernment Mode for extra ethical reflection prompts.

1. Data Management
   - Manage clients, cases, contracts, statutes, and more.
   - Use the main menu to select a data type and perform CRUD operations.

2. LLM Management
   - Go to 'LLM Management' to add, update, delete, or set the default LLM (local or API).

3. Profile Management
   - Use 'Profile Management' to create, update, or select practice area/jurisdiction profiles.
   - Profiles affect prompts and retrieval for your workflows.

4. Training & Feedback
   - Submit feedback or training examples to improve the system.
   - Export/import training data and train or evaluate models.

5. Backup & Restore
   - Use 'Backup' to save all data to a file, and 'Restore' to load it back.

6. Search/Filter
   - When listing any data type, use the search/filter option to find records by keyword.

7. Help & Info
   - Access this guide or the help menu anytime from the main menu.

8. Data Fetching
   - Use 'Data Fetching' to retrieve external data like statutes, cases, or constitutional articles.
   - Follow the prompts to specify parameters like jurisdiction or max results.

Tips:
- All actions are logged for traceability.
- Use the CLI menus to explore features interactively.
- For more details, see the README or Manual.md.

Press Enter to return to the main menu.
""")
    input() # Wait for user to press Enter


# --- Session State for Login/Logout ---
class SessionState:
    def __init__(self):
        self.current_user = None

    def login(self, kb: KnowledgeBase):
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        user = kb.authenticate_user(username, password)
        if user:
            self.current_user = user
            print(f"Logged in as {user['username']} (role: {user['role']})")
            logger.info(f"User logged in: {user['username']} ({user['role']})")
        else:
            print("Login failed. Invalid credentials.")
            logger.warning(f"Failed login attempt for username: {username}")

    def logout(self):
        if self.current_user:
            print(f"User '{self.current_user['username']}' logged out.")
            logger.info(f"User logged out: {self.current_user['username']}")
            self.current_user = None
        else:
            print("No user is currently logged in.")

    def require_login(self, required_roles=None):
        if not self.current_user:
            print("You must be logged in to perform this action.")
            return False
        if required_roles and self.current_user['role'] not in required_roles:
            print(f"Access denied. This action requires one of the following roles: {', '.join(required_roles)}.")
            return False
        return True


# --- Discernment State for Ethical Prompts ---
class DiscernmentState:
    def __init__(self):
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled
        print(f"Discernment Mode is now {'ON' if self.enabled else 'OFF'}.")

    def prompt(self, action_desc="proceed", tips=True):
        if not self.enabled:
            return True
        print("\n*** Discernment Mode Active ***")
        print(f"Before you {action_desc}, please pause and prayerfully consider:")
        if tips:
            print("- Is this action just, charitable, and prudent?\n- Does it align with Catholic moral teaching and the dignity of all involved?\n- Have you sought wise counsel or prayed for guidance?")
        confirm = input(f"Do you discern it is right to {action_desc}? (y/n): ").strip().lower()
        return confirm == 'y'


def discernment_prompt(action_desc, discernment_state):
    """Prompt user for ethical reflection before critical actions if Discernment Mode is enabled."""
    if discernment_state and getattr(discernment_state, 'enabled', False):
        print("\n--- Catholic Discernment Reflection ---")
        print(f"Before you {action_desc}, please pause and consider:\n- Does this action align with Catholic ethical principles (dignity, justice, truth, charity)?\n- Could this impact vulnerable persons or the common good?\n- Have you sought prayerful discernment or counsel if unsure?\n- Is this action necessary and proportionate?")
        confirm = input("Proceed with this action? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Action cancelled after discernment.")
            return False
    return True


def show_disclaimer_and_consent():
    print("""
==================== DISCLAIMER & CONSENT ====================
This system is an AI-enabled legal information and workflow tool.
It does NOT provide legal advice. All outputs must be reviewed by a qualified attorney.
By using this system, you consent to:
 - Logging of your actions for audit and compliance purposes
 - Adherence to the ethical guidelines and Catholic principles set forth in this firm
 - The use of your actions and feedback for ongoing system improvement
If you do not consent, please exit the CLI now.
==============================================================
""")
    consent = input("Do you consent to these terms? (y/n): ").strip().lower()
    if consent != 'y':
        print("Consent not given. Exiting CLI.")
        exit(0)


def ethical_guideline_record_menu(kb, discernment_state=None):
    while True:
        print("\n--- Ethical Guideline Records Menu ---")
        print("1. List Guidelines")
        print("2. Add Guideline")
        print("3. Update Guideline")
        print("4. Delete Guideline")
        print("0. Back")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            guidelines = kb.list_ethical_guideline_records()
            print(json.dumps(guidelines, indent=2))
        elif choice == "2":
            data = get_dict_from_input()
            if discernment_state and not discernment_state.prompt("add a new ethical guideline"): 
                print("Action cancelled.")
                continue
            try:
                kb.create_ethical_guideline_record(data)
                print("Guideline added.")
            except Exception as e:
                print_colored(f"Error: {e}", color='red')
        elif choice == "3":
            gid = input("Enter Guideline ID to update: ")
            updates = get_dict_from_input(prompt="Enter updates as key=value pairs:")
            if discernment_state and not discernment_state.prompt("update this ethical guideline"): 
                print("Action cancelled.")
                continue
            try:
                if kb.update_ethical_guideline_record(gid, updates):
                    print("Guideline updated.")
                else:
                    print("Guideline not found or update failed.")
            except Exception as e:
                print_colored(f"Error: {e}", color='red')
        elif choice == "4":
            gid = input("Enter Guideline ID to delete: ")
            if discernment_state and not discernment_state.prompt("delete this ethical guideline"): 
                print("Action cancelled.")
                continue
            try:
                if kb.delete_ethical_guideline_record(gid):
                    print("Guideline deleted.")
                else:
                    print("Guideline not found.")
            except Exception as e:
                print_colored(f"Error: {e}", color='red')
        elif choice == "0":
            break
        else:
            print("Invalid choice.")

def llm_qa_menu(kb, discernment_state=None):
    """Menu for LLM Q&A and drafting, with audit logging and feedback."""
    import datetime
    while True:
        print("\n--- LLM Q&A / Drafting Menu ---")
        llms = kb.list_llms()
        if not llms:
            print_colored("No LLMs configured. Please add one in LLM Management first.", color='yellow')
            return
        print("Available LLMs:")
        for idx, llm in enumerate(llms, 1):
            default_marker = "(Default)" if llm.get('is_default') else ""
            print(f"{idx}. {llm.get('name')} {default_marker} [{llm.get('type')}] (ID: {llm.get('id')})")
        print("0. Back")
        choice = input("Select LLM by number (or 0 to go back): ").strip()
        if choice == "0":
            break
        try:
            llm_idx = int(choice) - 1
            if llm_idx < 0 or llm_idx >= len(llms):
                print_colored("Invalid selection.", color='yellow')
                continue
            llm = llms[llm_idx]
        except Exception:
            print_colored("Invalid input.", color='yellow')
            continue
        while True:
            print("\nEnter your legal question, drafting prompt, or type 'back' to choose another LLM:")
            prompt = input("> ").strip()
            if prompt.lower() in ("back", "0", "exit"):
                break
            if not prompt:
                print_colored("Prompt cannot be empty.", color='yellow')
                continue
            # Discernment before sending prompt (optional, for sensitive queries)
            if discernment_state and discernment_state.enabled:
                if not discernment_state.prompt("submit this prompt to the LLM", tips=True):
                    print_colored("Action cancelled.", color='yellow')
                    continue
            print("\n[LLM is processing...]")
            try:
                from autonomous_defense_firm.llm_manager import run_llm_query
                response, explain = run_llm_query(llm, prompt)
                print_colored("\n--- LLM Response ---", color='blue')
                print(response)
                print_colored("\n--- Explainability ---", color='blue')
                print(explain or "No explainability info available.")
                # --- Audit log for LLM interaction ---
                from autonomous_defense_firm.audit import log_audit_event
                user = None
                try:
                    # Try to get user from session if available
                    user = getattr(globals().get('session', None), 'current_user', None)
                    if user and isinstance(user, dict):
                        user = user.get('username')
                except Exception:
                    user = None
                log_audit_event(
                    event_type="LLM_QUERY",
                    user=user,
                    details={
                        "llm_id": llm.get('id'),
                        "llm_name": llm.get('name'),
                        "prompt": prompt,
                        "response": response,
                        "explainability": explain,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                )
                # Discernment/ethical review after output
                if discernment_state and discernment_state.enabled:
                    print_colored("\nDiscernment: Please review the LLM output for ethical, legal, and Catholic alignment before use.", color='yellow')
                    feedback = input("Is this output appropriate and ethical? (y/n/feedback): ").strip().lower()
                    if feedback and feedback not in ('y', 'yes'):
                        print_colored("Thank you for your feedback. Please use caution with this output.", color='yellow')
                        # Log feedback for traceability
                        log_audit_event(
                            event_type="LLM_OUTPUT_FEEDBACK",
                            user=user,
                            details={
                                "llm_id": llm.get('id'),
                                "llm_name": llm.get('name'),
                                "prompt": prompt,
                                "response": response,
                                "feedback": feedback,
                                "timestamp": datetime.datetime.now().isoformat()
                            }
                        )
            except ImportError:
                print_colored("LLM integration module not found. Please implement run_llm_query in llm_manager.py.", color='red')
                break
            except Exception as e:
                print_colored(f"Error during LLM query: {e}", color='red')
                break


def main_cli():
    # Initialize KnowledgeBase and TrainingManager
    # Load existing data from default backup file if it exists.
    kb_backup_file = "knowledge_base_cli_data.json"
    kb = KnowledgeBase()
    try:
        kb.load_from_file(kb_backup_file)
        logger.info(f"KnowledgeBase data loaded from {kb_backup_file}")
    except FileNotFoundError:
        logger.info(f"{kb_backup_file} not found. Starting with an empty KnowledgeBase.")
    except Exception as e:
        logger.error(f"Error loading {kb_backup_file}: {e}. Starting with an empty KnowledgeBase.")

    tm = TrainingManager(knowledge_base=kb) # Pass kb to TrainingManager
    # Load training data if it exists
    training_backup_file = "training_manager_cli_data.json"
    if os.path.exists(training_backup_file):
        try:
            tm.import_training_data(training_backup_file) # Assumes this loads into tm.training_data
            logger.info(f"TrainingManager data loaded from {training_backup_file}")
        except Exception as e:
            logger.error(f"Error loading {training_backup_file} for TrainingManager: {e}")


    # Define main menu items with their corresponding KB methods
    # Tuple: (Display Name, create_fn, list_fn, update_fn, delete_fn, [specific_validation_fn if any])
    # Using None for update/delete if not applicable (e.g. for read-only views of statutes/cases from fetch)
    # The CRUD methods in KB are quite generic now.
    main_menu_items = [
        ("Documents", kb.create_document, kb.list_documents, kb.update_document, kb.delete_document, kb.validate_document),
        ("Statutes (Manual Entry)", kb.create_statute, kb.list_statutes, kb.update_statute, None, kb.validate_statute), # No delete for statutes shown, update only
        ("Cases (Manual Entry)", kb.create_case, kb.list_cases, kb.update_case, None, kb.validate_case), # No delete for cases shown
        ("Clients", kb.create_client, kb.list_clients, kb.update_client, kb.delete_client, kb.validate_client),
        ("Case Files", kb.create_case_file, kb.list_case_files, kb.update_case_file, kb.delete_case_file, kb.validate_case_file),
        ("Legal Research", kb.create_legal_research, kb.list_legal_research, kb.update_legal_research, kb.delete_legal_research, kb.validate_legal_research),
        ("Contracts", kb.create_contract, kb.list_contracts, kb.update_contract, kb.delete_contract, kb.validate_contract),
        ("Internal Docs", kb.create_internal_doc, kb.list_internal_docs, kb.update_internal_doc, kb.delete_internal_doc, kb.validate_internal_doc),
        ("Calendar Events", kb.create_calendar_event, kb.list_calendar_events, kb.update_calendar_event, kb.delete_calendar_event, kb.validate_calendar_event),
        ("Notes", kb.create_note, kb.list_notes, kb.update_note, kb.delete_note, kb.validate_note),
        ("Feedback Records (View/Manage)", kb.create_feedback, kb.list_feedback, kb.update_feedback, kb.delete_feedback, kb.validate_feedback), # Feedback also added via Training Menu
        ("Ethics Records", kb.create_ethics_record, kb.list_ethics_records, kb.update_ethics_record, kb.delete_ethics_record, kb.validate_ethics_record),
        ("Financial Records", kb.create_financial_record, kb.list_financial_records, kb.update_financial_record, kb.delete_financial_record, kb.validate_financial_record),
        ("Communication Logs", kb.create_communication_log, kb.list_communication_logs, kb.update_communication_log, kb.delete_communication_log, kb.validate_communication_log),
        ("Templates", kb.create_template, kb.list_templates, kb.update_template, kb.delete_template, kb.validate_template),
        ("External Data Records", kb.create_external_data, kb.list_external_data, kb.update_external_data, kb.delete_external_data, kb.validate_external_data),
    ]

    last_choice_index = len(main_menu_items)

    session = SessionState()
    discernment_state = DiscernmentState()
    show_disclaimer_and_consent()

    def print_main_menu():
        print("\n========== Main Menu ==========")
        for idx, (name, *_rest) in enumerate(main_menu_items, 1):
            print(f"{idx}. {name}")
        print(f"{last_choice_index+1}. LLM Management")
        print(f"{last_choice_index+2}. LLM Q&A / Drafting")
        print(f"{last_choice_index+3}. Profile Management")
        print(f"{last_choice_index+4}. Training & Feedback")
        print(f"{last_choice_index+5}. Data Fetching")
        print(f"{last_choice_index+6}. Ethical Guideline Records")
        print(f"{last_choice_index+7}. User Management")
        print(f"{last_choice_index+8}. Discernment Mode: {'ON' if discernment_state.enabled else 'OFF'} (toggle)")
        print(f"{last_choice_index+9}. Help/User Guide")
        print("0. Logout/Exit")

    try:
        while True:
            print_main_menu()
            choice = input("Select an option: ").strip().lower()
            if choice == "0":
                if discernment_state.prompt("logout and exit the CLI"):  # Discernment before exit
                    session.logout()
                    print("Goodbye.")
                    break
                else:
                    print("Logout cancelled.")
                    continue
            elif choice == str(last_choice_index+1):
                llm_menu(kb, discernment_state)
            elif choice == str(last_choice_index+2):
                llm_qa_menu(kb, discernment_state)
            elif choice == str(last_choice_index+3):
                profile_menu(kb, discernment_state)
            elif choice == str(last_choice_index+4):
                training_menu(tm, kb, discernment_state)
            elif choice == str(last_choice_index+5):
                data_fetch_menu(kb, discernment_state)
            elif choice == str(last_choice_index+6):
                ethical_guideline_record_menu(kb, discernment_state)
            elif choice == str(last_choice_index+7):
                user_management_menu(kb, discernment_state)
            elif choice == str(last_choice_index+8):
                discernment_state.toggle()
            elif choice == str(last_choice_index+9):
                user_guide()
            elif choice.isdigit() and 1 <= int(choice) <= len(main_menu_items):
                idx = int(choice) - 1
                name, create_fn, list_fn, update_fn, delete_fn, validate_fn = main_menu_items[idx]
                from autonomous_defense_firm.ethical_filter import check_ethics
                while True:
                    print(f"\n--- {name} Menu ---")
                    print("1. List")
                    print("2. Add")
                    print("3. Update")
                    if delete_fn:
                        print("4. Delete")
                    print("0. Back to Main Menu")
                    sub_choice = input(f"Choose an action ({name}): ").strip().lower()
                    if sub_choice == "1":
                        items = list_fn()
                        if items:
                            print(json.dumps(items, indent=2))
                        else:
                            print(f"No {name.lower()} found.")
                    elif sub_choice == "2":
                        data = get_dict_from_input()
                        # --- Ethical Filter integration ---
                        user = getattr(session, 'current_user', None)
                        result = check_ethics(data, action_type=f"create_{name.lower().replace(' ', '_')}", user=user)
                        if result['result'] == 'block':
                            print_colored(f"[ETHICAL BLOCK] {result['explanation']}", color='red')
                            log_audit_event("ETHICAL_BLOCK", user=user.get('username') if user else None, details=result)
                            continue
                        elif result['result'] == 'warn':
                            print_colored(f"[ETHICAL WARNING] {result['explanation']}", color='yellow')
                            override = input("Proceed anyway? (y/n): ").strip().lower()
                            if override != 'y':
                                print("Action cancelled due to ethical warning.")
                                log_audit_event("ETHICAL_WARN_CANCEL", user=user.get('username') if user else None, details=result)
                                continue
                            log_audit_event("ETHICAL_WARN_OVERRIDE", user=user.get('username') if user else None, details=result)
                        # --- End Ethical Filter integration ---
                        if validate_fn and not validate_fn(data):
                            print_colored("Validation failed. Please check your input.", color='yellow')
                            continue
                        if discernment_state.prompt(f"add a new {name.lower()}"):
                            try:
                                create_fn(data)
                                print_colored(f"{name} added.", color='green')
                            except Exception as e:
                                print_colored(f"Error: {e}", color='red')
                        else:
                            print_colored("Action cancelled.", color='yellow')
                    elif sub_choice == "3":
                        item_id = input("Enter ID to update: ").strip()
                        updates = get_dict_from_input(prompt="Enter updates as key=value pairs:")
                        if not updates:
                            print_colored("No updates provided.", color='yellow')
                            continue
                        # --- Ethical Filter integration ---
                        user = getattr(session, 'current_user', None)
                        result = check_ethics(updates, action_type=f"update_{name.lower().replace(' ', '_')}", user=user)
                        if result['result'] == 'block':
                            print_colored(f"[ETHICAL BLOCK] {result['explanation']}", color='red')
                            log_audit_event("ETHICAL_BLOCK", user=user.get('username') if user else None, details=result)
                            continue
                        elif result['result'] == 'warn':
                            print_colored(f"[ETHICAL WARNING] {result['explanation']}", color='yellow')
                            override = input("Proceed anyway? (y/n): ").strip().lower()
                            if override != 'y':
                                print("Action cancelled due to ethical warning.")
                                log_audit_event("ETHICAL_WARN_CANCEL", user=user.get('username') if user else None, details=result)
                                continue
                            log_audit_event("ETHICAL_WARN_OVERRIDE", user=user.get('username') if user else None, details=result)
                        # --- End Ethical Filter integration ---
                        if validate_fn and not validate_fn(updates):
                            print_colored("Validation failed. Please check your input.", color='yellow')
                            continue
                        if discernment_state.prompt(f"update this {name.lower()}"):
                            try:
                                if update_fn(item_id, updates):
                                    print_colored(f"{name} updated.", color='green')
                                else:
                                    print_colored(f"{name} not found or update failed.", color='yellow')
                            except Exception as e:
                                print_colored(f"Error: {e}", color='red')
                        else:
                            print_colored("Action cancelled.", color='yellow')
                    elif sub_choice == "4" and delete_fn:
                        item_id = input("Enter ID to delete: ").strip()
                        # --- Ethical Filter integration ---
                        user = getattr(session, 'current_user', None)
                        result = check_ethics({'id': item_id}, action_type=f"delete_{name.lower().replace(' ', '_')}", user=user)
                        if result['result'] == 'block':
                            print_colored(f"[ETHICAL BLOCK] {result['explanation']}", color='red')
                            log_audit_event("ETHICAL_BLOCK", user=user.get('username') if user else None, details=result)
                            continue
                        elif result['result'] == 'warn':
                            print_colored(f"[ETHICAL WARNING] {result['explanation']}", color='yellow')
                            override = input("Proceed anyway? (y/n): ").strip().lower()
                            if override != 'y':
                                print("Action cancelled due to ethical warning.")
                                log_audit_event("ETHICAL_WARN_CANCEL", user=user.get('username') if user else None, details=result)
                                continue
                            log_audit_event("ETHICAL_WARN_OVERRIDE", user=user.get('username') if user else None, details=result)
                        # --- End Ethical Filter integration ---
                        if discernment_state.prompt(f"delete this {name.lower()}"):
                            try:
                                if delete_fn(item_id):
                                    print_colored(f"{name} deleted.", color='green')
                                else:
                                    print_colored(f"{name} not found.", color='yellow')
                            except Exception as e:
                                print_colored(f"Error: {e}", color='red')
                        else:
                            print_colored("Action cancelled.", color='yellow')
                    elif sub_choice == "0" or sub_choice == "b":
                        break
                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("Invalid option. Please try again.")
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting CLI.")
    finally:
        try:
            kb.save_to_file(kb_backup_file)
            tm.export_training_data(training_backup_file)
            print("Data saved. Goodbye.")
        except Exception as e:
            print(f"Error saving data: {e}")