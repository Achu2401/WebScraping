import requests
import gspread
from google.oauth2.service_account import Credentials
import time


HUNTER_API_KEY = "df84ab000cb834276997bd637efe9975ef14d282"
COMPANY_DOMAINS = [
    "sbg.com.sa",
    "elseif.com.sa",
    "nesma-partners.com"
]

GOOGLE_SHEET_NAME = "Company Leads"
SERVICE_ACCOUNT_FILE = "credentials.json"

REQUEST_DELAY = 1.2  # seconds

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

def fetch_emails(domain):
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&limit=5&api_key={HUNTER_API_KEY}"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Hunter request error for {domain}: {response.status_code}")
        return []

    data = response.json()
    emails = data.get("data", {}).get("emails", [])
    
    results = []
    for e in emails:
        results.append([
            domain,
            e.get("first_name"),
            e.get("last_name"),
            e.get("position"),
            e.get("email"),
            e.get("linkedin"),
            "Hunter.io"
        ])
    return results

def main():
    sheet = connect_google_sheet()
    print("🚀 Starting lead extraction via Hunter.io...\n")

    for domain in COMPANY_DOMAINS:
        print(f"🔍 Processing: {domain}")
        leads = fetch_emails(domain)
        
        if not leads:
            print("   ⚠ No contacts found")
            time.sleep(REQUEST_DELAY)
            continue

        for lead in leads:
            sheet.append_row(lead, value_input_option="USER_ENTERED")
        
        print(f"   ✅ {len(leads)} contacts added\n")
        time.sleep(REQUEST_DELAY)

    print("🎉 Extraction completed successfully!")

if __name__ == "__main__":
    main()
