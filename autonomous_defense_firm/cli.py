"""
CLI entry point for the autonomous_defense_firm package.
"""
import argparse
from autonomous_defense_firm.legal_education import DEFAULT_CONFIG
from autonomous_defense_firm.knowledge_base import KnowledgeBase


def main():
    parser = argparse.ArgumentParser(description="Autonomous Defense Firm AI CLI")
    parser.add_argument('--info', action='store_true', help='Show project info and configuration')
    parser.add_argument('--fetch-tn-caselaw', action='store_true', help='Fetch Tennessee caselaw from free APIs')
    parser.add_argument('--fetch-tn-statutes', action='store_true', help='Fetch Tennessee statutes from Justia')
    parser.add_argument('--fetch-us-constitution', action='store_true', help='Fetch U.S. Constitution')
    parser.add_argument('--fetch-tn-constitution', action='store_true', help='Fetch Tennessee Constitution')
    parser.add_argument('--fetch-oyez', action='store_true', help='Fetch recent U.S. Supreme Court cases from Oyez')
    parser.add_argument('--gcloud-bucket', type=str, help='Google Cloud Storage bucket name for upload')
    parser.add_argument('--max-pages', type=int, default=2, help='Max pages to fetch from each API')
    parser.add_argument('--max-sections', type=int, default=5, help='Max TN statute sections to fetch')
    parser.add_argument('--max-cases', type=int, default=5, help='Max Oyez cases to fetch')
    parser.add_argument('--gcloud-key', type=str, help='Path to GCloud service account JSON key')
    args = parser.parse_args()

    if args.gcloud_key:
        import os
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.gcloud_key

    if args.info:
        print("Jurisdiction:", DEFAULT_CONFIG.jurisdiction)
        print("Areas of Law:", DEFAULT_CONFIG.areas_of_law)
        print("Skills:", DEFAULT_CONFIG.skills)
        print("User Role:", DEFAULT_CONFIG.user_role)
    elif args.fetch_tn_caselaw:
        kb = KnowledgeBase()
        print("Fetching Tennessee opinions from Caselaw Access Project...")
        cap_data = kb.fetch_caselaw_access_project(max_pages=args.max_pages)
        print(f"Fetched {len(cap_data)} opinions from CAP.")
        print("Fetching Tennessee opinions from CourtListener...")
        cl_data = kb.fetch_courtlistener(max_pages=args.max_pages)
        print(f"Fetched {len(cl_data)} opinions from CourtListener.")
        all_data = cap_data + cl_data
        print(f"Total documents fetched: {len(all_data)}")
        print("Starting human review...")
        approved = kb.human_review(all_data)
        print(f"Documents approved: {len(approved)}")
        if args.gcloud_bucket:
            print(f"Uploading to GCloud bucket: {args.gcloud_bucket}")
            success = kb.save_to_gcloud(approved, args.gcloud_bucket, "tn_caselaw.json")
            print("Upload successful." if success else "Upload failed.")
        else:
            print("No GCloud bucket specified. Skipping upload.")
    elif args.fetch_tn_statutes:
        kb = KnowledgeBase()
        print("Fetching Tennessee statutes from Justia...")
        statutes = kb.fetch_tn_statutes_justia(max_sections=args.max_sections)
        print(f"Fetched {len(statutes)} statute sections.")
        approved = kb.human_review(statutes)
        print(f"Documents approved: {len(approved)}")
        if args.gcloud_bucket:
            print(f"Uploading to GCloud bucket: {args.gcloud_bucket}")
            success = kb.save_to_gcloud(approved, args.gcloud_bucket, "tn_statutes.json")
            print("Upload successful." if success else "Upload failed.")
        else:
            print("No GCloud bucket specified. Skipping upload.")
    elif args.fetch_us_constitution:
        kb = KnowledgeBase()
        print("Fetching U.S. Constitution...")
        us_const = kb.fetch_us_constitution()
        approved = kb.human_review(us_const)
        if args.gcloud_bucket:
            print(f"Uploading to GCloud bucket: {args.gcloud_bucket}")
            success = kb.save_to_gcloud(approved, args.gcloud_bucket, "us_constitution.json")
            print("Upload successful." if success else "Upload failed.")
        else:
            print("No GCloud bucket specified. Skipping upload.")
    elif args.fetch_tn_constitution:
        kb = KnowledgeBase()
        print("Fetching Tennessee Constitution...")
        tn_const = kb.fetch_tn_constitution()
        approved = kb.human_review(tn_const)
        if args.gcloud_bucket:
            print(f"Uploading to GCloud bucket: {args.gcloud_bucket}")
            success = kb.save_to_gcloud(approved, args.gcloud_bucket, "tn_constitution.json")
            print("Upload successful." if success else "Upload failed.")
        else:
            print("No GCloud bucket specified. Skipping upload.")
    elif args.fetch_oyez:
        kb = KnowledgeBase()
        print("Fetching recent U.S. Supreme Court cases from Oyez...")
        oyez_cases = kb.fetch_oyez_supreme_court_cases(max_cases=args.max_cases)
        approved = kb.human_review(oyez_cases)
        if args.gcloud_bucket:
            print(f"Uploading to GCloud bucket: {args.gcloud_bucket}")
            success = kb.save_to_gcloud(approved, args.gcloud_bucket, "oyez_cases.json")
            print("Upload successful." if success else "Upload failed.")
        else:
            print("No GCloud bucket specified. Skipping upload.")
    else:
        print("Autonomous Defense Firm CLI. Use --info, --fetch-tn-caselaw, --fetch-tn-statutes, --fetch-us-constitution, --fetch-tn-constitution, --fetch-oyez, or see --help.")

if __name__ == "__main__":
    main()
