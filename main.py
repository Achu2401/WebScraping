"""
Apollo.io → Google Sheets Lead Extraction Script
------------------------------------------------
• Extract top 5 contacts per company
• Roles: Procurement, BD, Projects, Sales
• Store results in Google Sheets
"""

import requests
import time
import gspread
from google.oauth2.service_account import Credentials

# =========================
# CONFIGURATION
# =========================

APOLLO_API_KEY = "XV6jbu9Ew9SN1LLS5AJPiA"

COMPANY_DOMAINS = [

    "siemens.com",                # Siemens building systems
    "johnsoncontrols.com",        # Johnson Controls
    
  
]





APOLLO_URL = "https://api.apollo.io/v1/mixed_people/search"

GOOGLE_SHEET_NAME = "Apollo Leads"
SERVICE_ACCOUNT_FILE = "credentials.json"

REQUEST_DELAY = 1.2  # seconds (important for rate limits)

# =========================
# GOOGLE SHEETS SETUP
# =========================

def connect_google_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=scopes
    )

    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    return sheet


# =========================
# APOLLO API FUNCTIONS
# =========================

HEADERS = {
    "X-Api-Key": APOLLO_API_KEY,
    "Content-Type": "application/json"
}


def fetch_top_contacts(domain):
    payload = {
        "q_organization_domains": domain,
        "person_titles": [
            "Procurement",
            "Purchasing",
            "Business Development",
            "Projects",
            "Sales"
        ],
        "page": 1,
        "per_page": 5
    }

    response = requests.post(
        APOLLO_URL,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        print(f"❌ Apollo error for {domain}")
        return []

    return response.json().get("people", [])


def parse_people(people):
    parsed = []

    for p in people:
        org = p.get("organization", {})

        parsed.append([
            org.get("name"),
            org.get("website_url"),
            org.get("estimated_num_employees"),
            org.get("industry"),
            f"{p.get('first_name','')} {p.get('last_name','')}",
            p.get("title"),
            p.get("department"),
            p.get("email"),
            p.get("linkedin_url"),
            "Apollo.io"
        ])

    return parsed


# =========================
# MAIN EXECUTION
# =========================

def main():
    sheet = connect_google_sheet()

    print("🚀 Starting Apollo lead extraction...\n")

    for domain in COMPANY_DOMAINS:
        print(f"🔍 Processing: {domain}")

        people = fetch_top_contacts(domain)

        if not people:
            print("   ⚠ No contacts found")
            time.sleep(REQUEST_DELAY)
            continue

        rows = parse_people(people)

        for row in rows:
            sheet.append_row(row, value_input_option="USER_ENTERED")

        print(f"   ✅ {len(rows)} contacts added\n")

        time.sleep(REQUEST_DELAY)

    print("🎉 Extraction completed successfully!")


if __name__ == "__main__":
    main()
