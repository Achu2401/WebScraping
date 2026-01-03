import requests
import csv
from urllib.parse import urlparse

PERPLEXITY_API_KEY = "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"
HUNTER_API_KEY = "df84ab000cb834276997bd637efe9975ef14d282"
CSV_FILE = "leads.csv"
MAX_HUNTER_RESULTS = 5  # top contacts per domain
MAX_PERPLEXITY_RESULTS = 20# number of URLs to fetch


def search_perplexity(query, max_results=MAX_PERPLEXITY_RESULTS):
    """
    Get relevant company websites from Perplexity API
    """
    url = "https://api.perplexity.ai/search"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "max_results": max_results
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    
    # Extract URLs
    urls = []
    for r in data.get("results", []):
        link = r.get("url")
        if link:
            urls.append(link)
    return urls

def extract_domain(url):
    """
    Get domain from URL
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc or parsed_url.path  # fallback if no netloc

def get_hunter_contacts(domain, max_results=MAX_HUNTER_RESULTS):
    """
    Get top contacts from Hunter.io for a given domain
    """
    url = f"https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY,
        "limit": max_results
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    contacts = []
    for c in data.get("data", {}).get("emails", []):
        contact = {
            "Domain": domain,
            "Email": c.get("value"),
            "First Name": c.get("first_name"),
            "Last Name": c.get("last_name"),
            "Position": c.get("position"),
            "Seniority": c.get("seniority"),
            "LinkedIn": c.get("linkedin"),
            "Phone" : c.get("phone-number")
        }
        contacts.append(contact)
    return contacts

def main():
    query = input("Enter your search query: ")
    
    print("🚀 Searching Perplexity...")
    urls = search_perplexity(query)
    print(f"✅ Found {len(urls)} URLs")

    all_contacts = []
    for url in urls:
        domain = extract_domain(url)
        print(f"🔍 Fetching contacts for {domain}...")
        try:
            contacts = get_hunter_contacts(domain)
            if contacts:
                all_contacts.extend(contacts)
            else:
                print(f"⚠ No contacts found for {domain}")
        except Exception as e:
            print(f"❌ Hunter API error for {domain}: {e}")

    # Save results to CSV
    if all_contacts:
        keys = ["Domain", "Email", "First Name", "Last Name", "Position", "Seniority", "LinkedIn"]
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_contacts)
        print(f"🎉 Saved {len(all_contacts)} contacts to {CSV_FILE}")
    else:
        print("⚠ No contacts found.")

if __name__ == "__main__":
    main()
