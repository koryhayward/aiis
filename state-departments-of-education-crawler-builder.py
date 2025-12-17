import requests
from bs4 import BeautifulSoup
import csv
import os
import uuid
from datetime import datetime
import time

# --- Configuration ---
BASE_URL = "https://www.ed.gov"
DIRECTORY_URL = "https://www.ed.gov/contact-us/state-contacts"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

MD_TEMPLATE = """---
version: 1.0
type: state-department-of-education
uuid: "{uuid}"
author: "[[hayward-kory]]"
created: "[[{date}]]"
modified: "[[{date}]]"
template: "[[template-state-department-of-education]]"
name: "[[{name}]]"
website: {website}
headquarters: "{address}"
state: "{state_abbr}"
tags: 
- "#organization"
- "#organization/state-department-of-education"
---

# {name}
"""

def get_state_links():
    """Extracts state sub-page links from the main directory."""
    print(f"Fetching directory: {DIRECTORY_URL}")
    response = requests.get(DIRECTORY_URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    
    # Target <a> tags with the specific href pattern you identified
    for a in soup.find_all('a', href=True):
        href = a['href']
        if "/contact-us/state-contacts/" in href and len(href.split('/')) >= 4:
            # Avoid the main directory link itself
            if href != "/contact-us/state-contacts":
                links.append({'display_name': a.text.strip(), 'url': BASE_URL + href})
    
    print(f"Found {len(links)} state links.")
    return links

def scrape_state_details(url):
    """Parses contact details from the state sub-page."""
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {
        'full_name': "N/A",
        'address': "N/A",
        'state_abbr': "N/A",
        'website': "N/A",
        'phone': "N/A"
    }
    
    # Use the specific field classes from your screenshot
    name_div = soup.find('div', class_='field--name-field-state-contact-label2')
    if name_div: data['full_name'] = name_div.get_text(strip=True)
    
    # Extract Address Components
    street = soup.find('div', class_='field--name-field-ed-contact-street')
    city = soup.find('div', class_='field--name-field-ed-contact-city')
    zip_c = soup.find('div', class_='field--name-field-ed-contact-zip')
    
    if street and city and zip_c:
        data['address'] = f"{street.get_text(strip=True)}, {city.get_text(strip=True)}, {zip_c.get_text(strip=True)}"
    
    # State Abbreviation
    abbr_div = soup.find('div', class_='field--name-field-ed-state-abbreviation')
    if abbr_div: data['state_abbr'] = abbr_div.get_text(strip=True)
    
    # Website Link
    web_div = soup.find('div', class_='field--name-field-ed-contact-website')
    if web_div and web_div.find('a'):
        data['website'] = web_div.find('a')['href']
        
    # Phone Number
    phone_div = soup.find('div', class_='field--name-field-ed-state-contact-phone')
    if phone_div:
        item = phone_div.find('div', class_='field__item')
        if item: data['phone'] = item.get_text(strip=True)
        
    return data

def main():
    states = get_state_links()
    all_results = []
    
    if not os.path.exists('state-departments-of-education'):
        os.makedirs('state-departments-of-education')

    for state in states:
        try:
            print(f"Scraping {state['display_name']}...")
            details = scrape_state_details(state['url'])
            details['display_name'] = state['display_name']
            all_results.append(details)
            
            # Write Markdown
            safe_name = state['display_name'].replace(' ', '-').lower()
            with open(f"state-departments-of-education/{safe_name}-state-department-of-education.md", 'w', encoding='utf-8') as f:
                f.write(MD_TEMPLATE.format(
                    uuid=str(uuid.uuid4()),
                    date=datetime.now().strftime("%Y-%m-%d"),
                    name=state['display_name'],
                    website=details['website'],
                    address=details['address'],
                    state_abbr=details['state_abbr']
                ))
            
            # Politeness delay to avoid rate limiting
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error scraping {state['display_name']}: {e}")

    # Write CSV
    if all_results:
        keys = all_results[0].keys()
        with open('state_departments_final.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_results)
        print("Scraping complete. Files saved to /state-departments-of-education and state_departments_final.csv")

if __name__ == "__main__":
    main()