import requests
import csv
import time

# =========================
# CONFIGURATION
# =========================

SERPAPI_KEY = "a6aee5b377a95aeeeb57f09c3aca160796e32a20ffd2eaa7abb6836a46764096"
HUNTER_API_KEY = "df84ab000cb834276997bd637efe9975ef14d282"
SEARCH_QUERY = "Find out 400 relevant companies/leads who would like to sell their products/solutions to architects/consultants/contractors/engineering companies who are working on skyscraper projects in Saudi Arabia."
RESULTS_CSV = "leads.csv"
REQUEST_DELAY = 1  # seconds between API calls

# =========================
# FUNCTIONS
# =========================

def get_company_domains(query, num_results=20):
    """
    Use SerpApi to get company domains from Google search results
    """
    print(f"🔍 Scraping Google for query: {query}")
    url = f"https://serpapi.com/search.json"
    params = {
        "q": query,
        "engine": "google",
        "num": num_results,
        "api_key": SERPAPI_KEY
    }
    response = requests.get(url, params=params, timeout=30)
    if response.status_code != 200:
        print(f"❌ SerpApi error: {response.status_code}")
        return []

    data = response.json()
    domains = set()
    for result in data.get("organic_results", []):
        link = result.get("link")
        if link:
            # Extract domain from link
            domain = link.split("/")[2]
            domains.add(domain.lower())
    print(f"✅ Found {len(domains)} unique domains")
    return list(domains)

def get_hunter_contacts(domain, max_contacts=5):
    """
    Use Hunter.io to get top contacts for a domain
    """
    url = f"https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY,
        "limit": max_contacts
    }
    response = requests.get(url, params=params, timeout=30)
    if response.status_code != 200:
        print(f"❌ Hunter request error for {domain}: {response.status_code}")
        return []

    data = response.json()
    contacts = []
    for person in data.get("data", {}).get("emails", []):
        contacts.append([
            domain,
            person.get("value"),
            person.get("first_name"),
            person.get("last_name"),
            person.get("position"),
            person.get("department"),
            person.get("seniority"),
            person.get("linkedin") 
        ])
    return contacts

# =========================
# MAIN EXECUTION
# =========================

def main():
    # Step 1: Get company domains
    domains = get_company_domains(SEARCH_QUERY, num_results=30)
    if not domains:
        print("⚠ No domains found, exiting...")
        return

    # Step 2: Get Hunter.io contacts
    all_contacts = []
    for domain in domains:
        print(f"🔍 Fetching contacts for {domain}")
        contacts = get_hunter_contacts(domain)
        if contacts:
            all_contacts.extend(contacts)
            print(f"   ✅ {len(contacts)} contacts added")
        else:
            print(f"   ⚠ No contacts found for {domain}")
        time.sleep(REQUEST_DELAY)

    # Step 3: Save to CSV
    if all_contacts:
        with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Domain", "Email", "First Name", "Last Name", "Position", "Department", "Seniority"])
            writer.writerows(all_contacts)
        print(f"🎉 Saved {len(all_contacts)} contacts to {RESULTS_CSV}")
    else:
        print("⚠ No contacts to save")

if __name__ == "__main__":
    main()
