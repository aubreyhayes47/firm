"""
CLI entry point for the autonomous_defense_firm package.
Practice-area-neutral version: supports all law firm data types.
"""
import argparse
from autonomous_defense_firm.knowledge_base import KnowledgeBase
from autonomous_defense_firm.training import TrainingManager
# import sys # Not strictly needed for this version of cli.py
import uuid # For generating IDs if needed, though kb handles it internally
import logging
import json # For pretty printing dicts

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', # Added logger name
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__) # For CLI specific logs
kb_logger = logging.getLogger('KnowledgeBase') # If KB had its own logger
tm_logger = logging.getLogger('TrainingManager') # If TM had its own logger


def print_help():
    # Enhanced help message
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

Backup & Restore:
  - Save all current data to a JSON file (e.g., backup.json).
  - Load data from a previously saved JSON file.

Tips:
  - Search/Filter: When listing items, you can often filter by keyword.
  - Logging: Actions are logged to the console.
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
            print(f"Warning: Skipping malformed pair '{pair}'. Expected key=value format.")
    return data


def training_menu(tm: TrainingManager, kb: KnowledgeBase): # kb added for feedback linkage
    while True:
        print("\n--- Training & Feedback Menu ---")
        print("1. Submit Feedback / Training Example")
        print("2. Export Training Data to JSON")
        print("3. Import Training Data from JSON")
        print("4. Train a Model")
        print("5. List Trained Models")
        print("6. List Versions for a Model Type")
        print("7. Evaluate a Model")
        print("8. Save a Trained Model to File")
        print("9. Load a Trained Model from File")
        print("0. Back to Main Menu")
        
        sub_choice = input("Choose an action (Training): ").strip().lower()
        
        if sub_choice == "1":
            data_type = input("Enter data type (e.g., 'case_analysis', 'client_comm'): ").strip()
            print("Enter the data/features as key=value pairs (comma separated):")
            data_dict = get_dict_from_input()
            label = input("Enter the label/feedback/correct_answer: ").strip()
            try:
                # The TrainingManager's collect_training_example method also stores
                # it in the KnowledgeBase feedback list if the KB instance is passed to TM.
                tm.collect_training_example(data_type, data_dict, label)
                print("Feedback/training example submitted and stored.")
                logger.info(f"Training example collected: type={data_type}, data={data_dict}, label={label}")
            except Exception as e:
                print(f"Error submitting example: {e}")
                logger.error(f"Error in collect_training_example: {e}")
        
        elif sub_choice == "2":
            filename = input("Enter filename to export training data (e.g., training_export.json): ").strip()
            if not filename: filename = "training_data_export.json" # Default filename
            try:
                tm.export_training_data(filename)
                print(f"Training data exported to {filename}.")
                logger.info(f"Training data exported to {filename}")
            except Exception as e:
                print(f"Error exporting training data: {e}")
                logger.error(f"Error in export_training_data: {e}")

        elif sub_choice == "3":
            filename = input("Enter filename to import training data from (e.g., training_data.json): ").strip()
            if not filename:
                print("Filename cannot be empty.")
                continue
            try:
                tm.import_training_data(filename) # Assumes this adds to existing data or replaces
                print(f"Training data imported from {filename}. Total examples: {len(tm.training_data)}")
                logger.info(f"Training data imported from {filename}")
            except FileNotFoundError:
                print(f"Error: File '{filename}' not found.")
                logger.error(f"Import training data: File not found {filename}")
            except Exception as e:
                print(f"Error importing training data: {e}")
                logger.error(f"Error in import_training_data: {e}")

        elif sub_choice == "4":
            model_type = input("Enter model type to train (e.g., 'classification_model', 'ner_model'): ").strip()
            if not model_type:
                print("Model type cannot be empty.")
                continue
            print("Enter model parameters as key=value pairs (optional, comma separated):")
            param_dict = get_dict_from_input()
            try:
                if not tm.training_data:
                    print("Warning: No training data available to train the model.")
                    if input("Continue anyway (e.g., for a pre-configured model)? (y/n): ").lower() != 'y':
                        continue
                model_info = tm.train_model(model_type, param_dict)
                print(f"Model training initiated/completed for '{model_type}'. Info: {model_info}")
                logger.info(f"Model '{model_type}' trained with params {param_dict}. Info: {model_info}")
            except Exception as e:
                print(f"Error training model: {e}")
                logger.error(f"Error in train_model: {e}")
        
        elif sub_choice == "5":
            models = tm.list_models()
            if models:
                print("\nCurrently Trained Models:")
                for m_type in models:
                    print(f"- {m_type} (Details: {json.dumps(tm.models[m_type], indent=2)})")
            else:
                print("No models have been trained yet.")
        
        elif sub_choice == "6":
            model_type = input("Enter model type to list versions: ").strip()
            versions = tm.list_model_versions(model_type)
            if versions:
                print(f"\nVersions for Model Type '{model_type}':")
                for v_info in versions:
                    print(f"- Version {v_info['version']}: Trained on {v_info['model'].get('trained_on', 'N/A')} examples. Params: {v_info['model'].get('params')}")
            else:
                print(f"No versions found for model type '{model_type}' (or model type does not exist).")

        elif sub_choice == "7":
            model_type = input("Enter model type to evaluate: ").strip()
            if model_type not in tm.models:
                print(f"Model type '{model_type}' not found.")
                continue
            print("Enter test data as a list of key=value dicts. Each dict is one item.")
            print("Example: field1=val1,field2=val2;field1=otherval1,field2=otherval2") # Semicolon separated items
            raw_test_data_str = input("> ").strip()
            test_data_list = []
            if raw_test_data_str:
                items_str = raw_test_data_str.split(';')
                for item_str in items_str:
                    if item_str.strip():
                        test_data_list.append(get_dict_from_input(prompt=f"Parsing item: '{item_str.strip()}' (no new input needed, just shows parsing)"))
            
            if not test_data_list:
                print("No test data provided for evaluation.")
                continue
            try:
                eval_result = tm.evaluate_model(model_type, test_data_list)
                if eval_result:
                    print(f"Evaluation result for '{model_type}': {json.dumps(eval_result, indent=2)}")
                    logger.info(f"Model '{model_type}' evaluated. Result: {eval_result}")
                else:
                    print(f"Could not evaluate model '{model_type}'. It might not be trained or evaluation is not supported.")
            except Exception as e:
                print(f"Error evaluating model: {e}")
                logger.error(f"Error in evaluate_model: {e}")
        
        elif sub_choice == "8": # Save Model
            model_type = input("Enter model type to save: ").strip()
            if model_type not in tm.models:
                print(f"Model '{model_type}' not found in trained models.")
                continue
            path = input(f"Enter path to save model '{model_type}' (e.g., ./models/{model_type}.pkl): ").strip()
            if not path:
                print("Path cannot be empty.")
                continue
            try:
                if tm.save_model(model_type, path):
                    print(f"Model '{model_type}' saved to {path}.")
                    logger.info(f"Model '{model_type}' saved to {path}")
                else:
                    print(f"Failed to save model '{model_type}'. It might not exist.") # Should be caught above
            except Exception as e:
                print(f"Error saving model: {e}")
                logger.error(f"Error saving model '{model_type}' to {path}: {e}")

        elif sub_choice == "9": # Load Model
            model_type = input("Enter model type to load (this will be its identifier): ").strip()
            path = input(f"Enter path to load model '{model_type}' from (e.g., ./models/{model_type}.pkl): ").strip()
            if not model_type or not path:
                print("Model type and path cannot be empty.")
                continue
            try:
                loaded_model = tm.load_model(model_type, path)
                if loaded_model:
                    print(f"Model '{model_type}' loaded from {path}. Details: {json.dumps(loaded_model, indent=2)}")
                    logger.info(f"Model '{model_type}' loaded from {path}")
                else:
                    print(f"Failed to load model from {path}. File might not exist or is invalid.")
            except Exception as e:
                print(f"Error loading model: {e}")
                logger.error(f"Error loading model '{model_type}' from {path}: {e}")

        elif sub_choice == "0" or sub_choice == "b":
            break
        else:
            print("Invalid choice in Training Menu. Please try again.")


def llm_menu(kb: KnowledgeBase):
    while True:
        print("\n--- LLM Management Menu ---")
        print("1. List LLMs")
        print("2. Add LLM")
        print("3. Update LLM") # KnowledgeBase now has ID-based LLM management
        print("4. Delete LLM") # KnowledgeBase now has ID-based LLM management
        print("5. Set Default LLM") # KnowledgeBase now has ID-based LLM management
        print("6. Show Default LLM")
        # The llm_manager.py also has test_llm - could be added here if kb exposes it.
        print("0. Back to Main Menu")
        
        sub_choice = input("Choose an action (LLM Management): ").strip().lower()

        if sub_choice == "1":
            llms = kb.list_llms() # Assumes kb.list_llms() returns the list of LLM dicts
            if llms:
                print("\nAvailable LLM Configurations:")
                for idx, llm_conf in enumerate(llms):
                    default_marker = "(Default)" if llm_conf.get('is_default') else ""
                    # Displaying relevant fields. KB's LLM structure: name, type, model_path/api_url, api_key, id, is_default
                    print(f"  {idx+1}. ID: {llm_conf.get('id')}")
                    print(f"     Name: {llm_conf.get('name')} {default_marker}")
                    print(f"     Type: {llm_conf.get('type')}")
                    if llm_conf.get('type') == 'local':
                        print(f"     Path: {llm_conf.get('model_path', 'N/A')}") # From original KB structure
                    elif llm_conf.get('type') == 'api':
                        print(f"     URL: {llm_conf.get('api_url', 'N/A')}") # From original KB structure
                        print(f"     API Key: {'********' if llm_conf.get('api_key') else 'Not Set'}")
                    print("-" * 20)
            else:
                print("No LLM configurations found.")
        
        elif sub_choice == "2":
            name = input("Enter LLM name: ").strip()
            llm_type = input("Enter LLM type ('local' or 'api'): ").strip().lower()
            llm_data = {'name': name, 'type': llm_type}
            if llm_type == 'local':
                llm_data['model_path'] = input("Enter local model path: ").strip()
            elif llm_type == 'api':
                llm_data['api_url'] = input("Enter API URL: ").strip()
                llm_data['api_key'] = input("Enter API key (leave blank if none): ").strip()
            else:
                print("Invalid LLM type. Must be 'local' or 'api'.")
                continue
            
            is_default_input = input("Set as default LLM? (y/n): ").strip().lower()
            is_default = is_default_input == 'y'
            llm_data['is_default'] = is_default # Add to the dict for create_llm

            try:
                created_llm = kb.create_llm(llm_data) # kb.create_llm assigns an ID and handles is_default internally
                if is_default and created_llm.get('id'): # If create_llm doesn't handle setting default across list
                    kb.set_default_llm(created_llm['id']) # Ensure only this one is default
                print(f"LLM '{name}' added with ID '{created_llm.get('id')}'.")
                logger.info(f"LLM added: {created_llm}")
            except ValueError as ve:
                print(f"Error adding LLM: {ve}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                logger.error(f"Error adding LLM: {e}")

        elif sub_choice == "3": # Update LLM
            llm_id = input("Enter ID of LLM to update: ").strip()
            if not kb.get_profile_by_id(llm_id): # Simple check if ID might exist (not perfect for LLMs)
                 # A get_llm_by_id would be better in KB
                llm_exists = any(l.get('id') == llm_id for l in kb.list_llms())
                if not llm_exists:
                    print(f"LLM with ID '{llm_id}' not found.")
                    continue

            print("Enter updates as key=value pairs (e.g., name=NewName,model_path=/new/path). Blank to skip.")
            updates = get_dict_from_input()
            if 'is_default' in updates: # Handle boolean conversion for 'is_default'
                updates['is_default'] = updates['is_default'].lower() in ['true', 'y', 'yes', '1']
            
            if not updates:
                print("No updates provided.")
                continue
            try:
                if kb.update_llm(llm_id, updates):
                    print(f"LLM '{llm_id}' updated successfully.")
                    logger.info(f"LLM '{llm_id}' updated with {updates}")
                else: # Should have been caught by check above
                    print(f"Failed to update LLM '{llm_id}'. Not found.")
            except ValueError as ve:
                print(f"Error updating LLM: {ve}")
            except Exception as e:
                print(f"An unexpected error occurred during update: {e}")
                logger.error(f"Error updating LLM '{llm_id}': {e}")
        
        elif sub_choice == "4": # Delete LLM
            llm_id = input("Enter ID of LLM to delete: ").strip()
            try:
                if kb.delete_llm(llm_id):
                    print(f"LLM '{llm_id}' deleted successfully.")
                    logger.info(f"LLM '{llm_id}' deleted")
                else:
                    print(f"LLM with ID '{llm_id}' not found.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                logger.error(f"Error deleting LLM '{llm_id}': {e}")

        elif sub_choice == "5": # Set Default LLM
            llm_id = input("Enter ID of LLM to set as default: ").strip()
            try:
                if kb.set_default_llm(llm_id):
                    print(f"LLM '{llm_id}' is now the default.")
                    logger.info(f"LLM '{llm_id}' set as default.")
                else:
                    print(f"LLM with ID '{llm_id}' not found or failed to set as default.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                logger.error(f"Error setting default LLM to '{llm_id}': {e}")

        elif sub_choice == "6": # Show Default LLM
            default_llm = kb.get_default_llm()
            if default_llm:
                print("\nCurrent Default LLM:")
                print(f"  ID: {default_llm.get('id')}")
                print(f"  Name: {default_llm.get('name')}")
                print(f"  Type: {default_llm.get('type')}")
                if default_llm.get('type') == 'local':
                    print(f"  Path: {default_llm.get('model_path', 'N/A')}")
                elif default_llm.get('type') == 'api':
                    print(f"  URL: {default_llm.get('api_url', 'N/A')}")
            else:
                print("No default LLM is currently set.")
        
        elif sub_choice == "0" or sub_choice == "b":
            break
        else:
            print("Invalid choice in LLM Menu. Please try again.")


def profile_menu(kb: KnowledgeBase):
    kb._ensure_profiles_initialized() # Ensure profile attributes exist

    while True:
        print("\n--- Practice Area & Jurisdiction Profiles Menu ---")
        print("1. List Profiles")
        print("2. Add Profile")
        print("3. Update Profile")
        print("4. Delete Profile")
        print("5. Set Active Profile")
        print("6. Show Active Profile")
        print("0. Back to Main Menu")
        
        sub_choice = input("Choose an action (Profiles): ").strip().lower()

        if sub_choice == "1":
            profiles = kb.list_profiles()
            active_profile = kb.get_active_profile()
            if profiles:
                print("\nAvailable Profiles:")
                for idx, p in enumerate(profiles):
                    active_marker = "(Active)" if active_profile and active_profile.get('id') == p.get('id') else ""
                    print(f"  {idx+1}. ID: {p.get('id')}")
                    print(f"     Name: {p.get('name')} {active_marker}")
                    print(f"     Jurisdiction: {p.get('jurisdiction', 'N/A')}")
                    print(f"     Practice Area: {p.get('practice_area', 'N/A')}")
                    print(f"     Prompt Template: {(p.get('prompt_template', 'None')[:50] + '...') if p.get('prompt_template') and len(p.get('prompt_template', '')) > 50 else p.get('prompt_template', 'None')}")
                    print("-" * 20)
            else:
                print("No profiles found.")
        
        elif sub_choice == "2":
            print("Adding a new profile...")
            name = input("Enter profile name (e.g., 'TN Criminal Defense'): ").strip()
            jurisdiction = input("Enter jurisdiction (e.g., 'Tennessee'): ").strip()
            practice_area = input("Enter practice area (e.g., 'Criminal Law'): ").strip()
            prompt_template = input("Enter custom prompt template (optional, can be long): ").strip()
            
            profile_data = {'name': name, 'jurisdiction': jurisdiction, 'practice_area': practice_area}
            if prompt_template: # Only add if provided
                profile_data['prompt_template'] = prompt_template
            
            try:
                created_profile = kb.create_profile(profile_data)
                print(f"Profile '{name}' created with ID '{created_profile.get('id')}'.")
                logger.info(f"Profile created: {created_profile}")
            except ValueError as ve:
                print(f"Error creating profile: {ve}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                logger.error(f"Error creating profile: {e}")

        elif sub_choice == "3": # Update Profile
            profile_id = input("Enter ID of profile to update: ").strip()
            if not kb.get_profile_by_id(profile_id):
                 print(f"Profile with ID '{profile_id}' not found.")
                 continue
            print(f"Updating profile ID: {profile_id}. Enter new values or leave blank to keep current.")
            updates = get_dict_from_input(prompt="Enter updates (e.g., name=New Name,jurisdiction=New Jurisdiction):")
            if not updates:
                print("No updates provided.")
                continue
            try:
                if kb.update_profile(profile_id, updates):
                    print(f"Profile '{profile_id}' updated.")
                    logger.info(f"Profile '{profile_id}' updated with {updates}")
                else: # Should be caught by get_profile_by_id
                    print(f"Failed to update profile '{profile_id}'. Not found.")
            except ValueError as ve:
                print(f"Error updating profile: {ve}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                logger.error(f"Error updating profile '{profile_id}': {e}")

        elif sub_choice == "4": # Delete Profile
            profile_id = input("Enter ID of profile to delete: ").strip()
            try:
                if kb.delete_profile(profile_id):
                    print(f"Profile '{profile_id}' deleted.")
                    logger.info(f"Profile '{profile_id}' deleted.")
                else:
                    print(f"Profile with ID '{profile_id}' not found.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                logger.error(f"Error deleting profile '{profile_id}': {e}")
        
        elif sub_choice == "5": # Set Active Profile
            profile_id = input("Enter ID of profile to set as active: ").strip()
            try:
                if kb.set_active_profile(profile_id):
                    # kb.set_active_profile already prints a message
                    logger.info(f"Active profile set to '{profile_id}'.")
                else: # kb.set_active_profile prints if not found
                    pass
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                logger.error(f"Error setting active profile to '{profile_id}': {e}")

        elif sub_choice == "6": # Show Active Profile
            active_profile = kb.get_active_profile()
            if active_profile:
                print("\nCurrent Active Profile:")
                print(f"  ID: {active_profile.get('id')}")
                print(f"  Name: {active_profile.get('name')}")
                print(f"  Jurisdiction: {active_profile.get('jurisdiction', 'N/A')}")
                print(f"  Practice Area: {active_profile.get('practice_area', 'N/A')}")
                print(f"  Prompt Template: {(active_profile.get('prompt_template', 'None')[:70] + '...') if active_profile.get('prompt_template') and len(active_profile.get('prompt_template','')) > 70 else active_profile.get('prompt_template', 'None')}")
            else:
                print("No active profile is currently set.")
        
        elif sub_choice == "0" or sub_choice == "b":
            break
        else:
            print("Invalid choice in Profiles Menu. Please try again.")


def user_guide(): # Simple user guide from original cli.py
    print("""
Welcome to the Autonomous Law Firm CLI Interactive User Guide!
-------------------------------------------------------------
This guide will walk you through the main features of the system step by step.

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


def data_fetch_menu(kb: KnowledgeBase):
    while True:
        print("\n--- External Data Fetching Menu ---")
        print("1. Fetch Statutes (e.g., for Tennessee)")
        print("2. Fetch Case Law (from CAP and CourtListener)")
        print("3. Fetch Constitution (e.g., US Constitution)")
        print("4. Run Full Data Ingestion Pipeline (Fetch & Store to GCloud - requires setup)")
        print("5. Run Integration Test (Small fetch & Store to GCloud - requires setup)")
        print("6. Run DEBUG Data Ingestion Pipeline (Verbose, auto-approves - requires setup)")
        print("0. Back to Main Menu")
        
        sub_choice = input("Choose an action (Data Fetching): ").strip().lower()

        if sub_choice == "1":
            jurisdiction = input("Enter jurisdiction (e.g., 'Tennessee', default: Tennessee): ").strip() or "Tennessee"
            max_items_str = input("Max sections/items to fetch (default 10): ").strip()
            max_items = int(max_items_str) if max_items_str.isdigit() else 10
            try:
                statutes = kb.fetch_data('statutes', jurisdiction=jurisdiction, max_items=max_items) # Using max_items
                if statutes:
                    print(f"\nFetched {len(statutes)} statutes for '{jurisdiction}':")
                    for s in statutes[:3]: # Print first 3 samples
                        print(f"  Title: {s.get('title', 'N/A')[:80]}")
                        print(f"  Text Snippet: {(s.get('text', '')[:100] + '...') if s.get('text') else 'N/A'}\n")
                    # Optionally save these to the KB's internal documents or statutes list
                    # For example:
                    # for s_data in statutes:
                    #     kb.create_statute({'section': s_data.get('section_number','N/A'), 'title': s_data.get('title'), 'text': s_data.get('text')})
                    # print(f"Statutes also added to internal KnowledgeBase list.")
                else:
                    print(f"No statutes fetched for '{jurisdiction}'.")
            except Exception as e:
                print(f"Error fetching statutes: {e}")
                logger.error(f"Error fetching statutes for {jurisdiction}: {e}")
        
        elif sub_choice == "2":
            court_jurisdiction = input("Enter court/jurisdiction (e.g., 'Tennessee', 'Federal', default: Tennessee): ").strip() or "Tennessee"
            max_pages_str = input("Max pages per source (default 2): ").strip() # Smaller default for CLI demo
            max_pages = int(max_pages_str) if max_pages_str.isdigit() else 2
            try:
                cases = kb.fetch_data('cases', court_jurisdiction=court_jurisdiction, max_pages_per_source=max_pages)
                if cases:
                    print(f"\nFetched {len(cases)} case law documents for '{court_jurisdiction}':")
                    for c_idx, c in enumerate(cases[:3]): # Print first 3 samples
                        name = c.get('caseName') or c.get('case_name') or c.get('title', f"Case {c_idx+1}")
                        source = c.get('data_source', 'Unknown Source')
                        print(f"  Source: {source} | Name: {name[:80]}")
                        # print(f"  Full Data: {json.dumps(c, indent=2, default=str)}") # If you want to see all data
                        print("-" * 10)
                else:
                    print(f"No case law fetched for '{court_jurisdiction}'.")
            except Exception as e:
                print(f"Error fetching case law: {e}")
                logger.error(f"Error fetching case law for {court_jurisdiction}: {e}")

        elif sub_choice == "3":
            country = input("Enter country for constitution (e.g., 'US', default: US): ").strip().upper() or "US"
            try:
                constitution_parts = kb.fetch_data('constitution', country=country)
                if constitution_parts:
                    print(f"\nFetched {len(constitution_parts)} parts of the {country} Constitution:")
                    for part in constitution_parts[:3]: # Print first 3 samples
                        print(f"  Title: {part.get('title', 'N/A')}")
                        print(f"  Text Snippet: {(part.get('text', '')[:100] + '...') if part.get('text') else 'N/A'}\n")
                else:
                    print(f"No constitution data fetched for '{country}'.")
            except Exception as e:
                print(f"Error fetching constitution: {e}")
                logger.error(f"Error fetching constitution for {country}: {e}")
        
        elif sub_choice == "4": # Run Full Pipeline
            print("This will fetch data and attempt to store it in Google Cloud Storage.")
            bucket = input("Enter GCloud bucket name: ").strip()
            if not bucket:
                print("Bucket name is required.")
                continue
            cj = input("Enter Case Law Jurisdiction (default: Tennessee): ").strip() or "Tennessee"
            sj = input("Enter Statute Jurisdiction (default: Tennessee): ").strip() or "Tennessee"
            mp = input("Max Case Pages per source (default: 2): ").strip()
            ms = input("Max Statute Items (default: 2): ").strip()
            auto_approve = input("Auto-approve human review steps? (y/n, default: n): ").strip().lower() == 'y'

            try:
                kb.run_pipeline(
                    court_jurisdiction=cj, max_case_pages_per_source=int(mp) if mp.isdigit() else 2,
                    statute_jurisdiction=sj, max_statute_items=int(ms) if ms.isdigit() else 2,
                    bucket_name=bucket, auto_approve_review=auto_approve
                )
            except Exception as e:
                print(f"Pipeline execution error: {e}")
                logger.error(f"Pipeline error: {e}")
        
        elif sub_choice == "5": # Integration Test
            bucket = input("Enter GCloud bucket name for test (e.g., your-test-bucket): ").strip()
            if not bucket:
                print("Test bucket name is required.")
                continue
            print("Running small integration test (fetch 1 page/item, auto-approve)...")
            try:
                kb.test_integration(bucket_name_to_use=bucket)
            except Exception as e:
                print(f"Integration test error: {e}")
                logger.error(f"Integration test error: {e}")
        
        elif sub_choice == "6": # Debug Pipeline
            print("This will run the DEBUG pipeline with verbose output and auto-approvals.")
            bucket = input("Enter GCloud bucket name for DEBUG (e.g., your-debug-bucket): ").strip()
            if not bucket:
                print("Bucket name for DEBUG is required.")
                continue
            # Using small defaults for debug pipeline
            try:
                kb.run_debug_pipeline(bucket_name=bucket, max_case_pages_per_source=1, max_statute_items=1)
            except Exception as e:
                print(f"DEBUG Pipeline execution error: {e}")
                logger.error(f"DEBUG Pipeline error: {e}")

        elif sub_choice == "0" or sub_choice == "b":
            break
        else:
            print("Invalid choice in Data Fetching Menu. Please try again.")


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

    try: # Wrap main loop in try-finally to save data on exit
        while True:
            print("\n======= Autonomous Law Firm CLI - Main Menu =======")
            for idx, (label, *_) in enumerate(main_menu_items, 1):
                print(f"{idx}. Manage {label}")
            
            print(f"\n--- Other Actions ---")
            print(f"{last_choice_index + 1}. Training & Feedback Menu")
            print(f"{last_choice_index + 2}. LLM Management Menu")
            print(f"{last_choice_index + 3}. Profile Management Menu")
            print(f"{last_choice_index + 4}. Data Fetching Menu")
            print(f"{last_choice_index + 5}. Backup All Data (to {kb_backup_file})")
            print(f"{last_choice_index + 6}. Restore All Data (from {kb_backup_file})")
            print(f"{last_choice_index + 7}. General Help / Info")
            print(f"{last_choice_index + 8}. User Guide / Walkthrough")
            print(f"{last_choice_index + 9}. Exit CLI")

            choice_str = input(f"\nSelect an option (1-{last_choice_index + 9}): ").strip().lower()

            if not choice_str.isdigit():
                if choice_str in ['q', 'exit', str(last_choice_index + 9)]: # Handle 'q' or 'exit' as exit command
                     choice_str = str(last_choice_index + 9)
                else:
                    print("Invalid input. Please enter a number.")
                    continue
            
            choice = int(choice_str)

            if 1 <= choice <= last_choice_index:
                # Generic CRUD menu for selected data type
                item_name, create_fn, list_fn, update_fn, delete_fn, validate_fn = main_menu_items[choice - 1]
                
                while True: # Inner loop for CRUD operations on the selected item
                    print(f"\n--- {item_name} Management ---")
                    print("1. List All")
                    print("2. Add New")
                    if update_fn: print("3. Update Existing")
                    if delete_fn: print("4. Delete Existing")
                    print("5. Search/Filter List") # Added search/filter
                    print("0. Back to Main Menu")

                    sub_m_choice = input(f"Choose action for {item_name}: ").strip().lower()

                    if sub_m_choice == "1": # List
                        items = list_fn()
                        print(f"\nTotal {item_name.lower()}: {len(items)}")
                        if items:
                            for item_idx, item_data in enumerate(items):
                                print(f"  Item {item_idx+1} (ID: {item_data.get('id', 'N/A')}):")
                                # Pretty print dictionary
                                print(json.dumps(item_data, indent=4, default=str)) # Use default=str for non-serializable
                                print("-" * 10)
                        else:
                            print(f"No {item_name.lower()} found.")
                    
                    elif sub_m_choice == "2": # Add
                        print(f"\nAdding new {item_name.lower()}. Please provide details.")
                        data_dict = get_dict_from_input()
                        try:
                            # Perform validation if a specific validation function is provided
                            if validate_fn: validate_fn(data_dict)
                            created_item = create_fn(data_dict)
                            print(f"{item_name} created with ID: {created_item.get('id')}")
                            logger.info(f"Created {item_name}: {created_item}")
                        except ValueError as ve:
                            print(f"Validation Error: {ve}")
                        except Exception as e:
                            print(f"Error creating {item_name.lower()}: {e}")
                            logger.error(f"Error creating {item_name}: {e}")
                    
                    elif sub_m_choice == "3" and update_fn: # Update
                        item_id = input(f"Enter ID of {item_name.lower()} to update: ").strip()
                        # Check if item exists (optional, update_fn should handle not found)
                        print(f"Enter updates for {item_name.lower()} ID {item_id} (key=value, comma separated):")
                        updates_dict = get_dict_from_input()
                        if not updates_dict:
                            print("No updates provided.")
                            continue
                        try:
                            # Fetch current item to validate against if validate_fn exists
                            # current_item = next((i for i in list_fn() if i.get('id') == item_id), None)
                            # if current_item and validate_fn:
                            #     validate_fn({**current_item, **updates_dict}) # Validate merged data
                            
                            if update_fn(item_id, updates_dict):
                                print(f"{item_name} with ID '{item_id}' updated.")
                                logger.info(f"Updated {item_name} ID {item_id} with {updates_dict}")
                            else:
                                print(f"{item_name} with ID '{item_id}' not found or update failed.")
                        except ValueError as ve:
                            print(f"Validation Error during update: {ve}")
                        except Exception as e:
                            print(f"Error updating {item_name.lower()}: {e}")
                            logger.error(f"Error updating {item_name} ID {item_id}: {e}")

                    elif sub_m_choice == "4" and delete_fn: # Delete
                        item_id = input(f"Enter ID of {item_name.lower()} to delete: ").strip()
                        # Optional: Confirm before deleting
                        if input(f"Are you sure you want to delete {item_name} ID '{item_id}'? (y/n): ").lower() != 'y':
                            continue
                        try:
                            if delete_fn(item_id):
                                print(f"{item_name} with ID '{item_id}' deleted.")
                                logger.info(f"Deleted {item_name} ID {item_id}")
                            else:
                                print(f"{item_name} with ID '{item_id}' not found.")
                        except Exception as e:
                            print(f"Error deleting {item_name.lower()}: {e}")
                            logger.error(f"Error deleting {item_name} ID {item_id}: {e}")
                    
                    elif sub_m_choice == "5": # Search/Filter
                        keyword = input("Enter keyword to search/filter by (case insensitive): ").strip().lower()
                        all_items = list_fn()
                        if keyword:
                            filtered_items = [
                                item for item in all_items 
                                if any(keyword in str(value).lower() for value in item.values())
                            ]
                        else: # If no keyword, show all (same as list)
                            filtered_items = all_items
                        
                        print(f"\nFound {len(filtered_items)} {item_name.lower()} matching '{keyword}':")
                        if filtered_items:
                            for item_idx, item_data in enumerate(filtered_items):
                                print(f"  Item {item_idx+1} (ID: {item_data.get('id', 'N/A')}):")
                                print(json.dumps(item_data, indent=4, default=str))
                                print("-" * 10)
                        else:
                            print("No matching items found.")

                    elif sub_m_choice == "0" or sub_m_choice == "b":
                        break
                    else:
                        print("Invalid choice. Please try again.")
            
            # Handle other main menu choices
            elif choice == last_choice_index + 1:
                training_menu(tm, kb)
            elif choice == last_choice_index + 2:
                llm_menu(kb)
            elif choice == last_choice_index + 3:
                profile_menu(kb)
            elif choice == last_choice_index + 4:
                data_fetch_menu(kb)
            elif choice == last_choice_index + 5: # Backup
                try:
                    kb.save_to_file(kb_backup_file) # KB saves itself
                    tm.export_training_data(training_backup_file) # TM saves its training data
                    print(f"All data backed up to {kb_backup_file} and {training_backup_file}.")
                    logger.info(f"Data backed up to {kb_backup_file} and {training_backup_file}")
                except Exception as e:
                    print(f"Error during backup: {e}")
                    logger.error(f"Backup error: {e}")
            elif choice == last_choice_index + 6: # Restore
                try:
                    if input(f"Restore will overwrite current data. Continue? (y/n): ").lower() == 'y':
                        kb.load_from_file(kb_backup_file) # KB loads itself
                        tm.import_training_data(training_backup_file) # TM loads its training data
                        print(f"All data restored from {kb_backup_file} and {training_backup_file}.")
                        logger.info(f"Data restored from {kb_backup_file} and {training_backup_file}")
                    else:
                        print("Restore cancelled.")
                except FileNotFoundError:
                    print(f"Error: One or both backup files ({kb_backup_file}, {training_backup_file}) not found.")
                except Exception as e:
                    print(f"Error during restore: {e}")
                    logger.error(f"Restore error: {e}")
            elif choice == last_choice_index + 7:
                print_help()
            elif choice == last_choice_index + 8:
                user_guide()
            elif choice == last_choice_index + 9:
                print("Exiting CLI...")
                break # Exit main while loop
            else:
                print("Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\nCLI interrupted by user. Exiting.")
    finally:
        # Attempt to save data on any exit (normal or interrupt)
        print(f"\nAttempting to save data before final exit...")
        try:
            kb.save_to_file(kb_backup_file)
            tm.export_training_data(training_backup_file)
            print(f"Data successfully saved to {kb_backup_file} and {training_backup_file}.")
            logger.info("Final data save successful on exit.")
        except Exception as e:
            print(f"Could not save data on exit: {e}")
            logger.error(f"Final data save failed on exit: {e}")
        print("Goodbye!")


if __name__ == "__main__":
    # This allows running the CLI directly using `python -m autonomous_defense_firm.cli`
    # or if this script itself is run.
    
    # Argument parsing (optional, for future enhancements like specifying a backup file)
    parser = argparse.ArgumentParser(description="Autonomous Law Firm CLI.")
    # Example: parser.add_argument('--backup-file', type=str, help='Specify a backup file to load/save.')
    args = parser.parse_args() # Parse arguments if any are defined

    main_cli()