import csv
import os
import uuid
from datetime import datetime

INPUT_CSV = 'state-boards-of-education-init.csv'
OUTPUT_DIR = 'state-boards-of-education'
DATE_TODAY = datetime.now().strftime('%Y-%m-%d')

def create_slug(name):
    return name.lower().replace(' ', '-')

def generate_markdown(state_name, abbreviation, url):
    file_uuid = str(uuid.uuid4())
    slug = create_slug(state_name)
    
    url_line = f"website: {url}" if url else "website: "
    
    content = f"""---
version: 1.0
type: state-board-of-education
uuid: "{file_uuid}"
author: "[[hayward-kory]]"
created: "[[{DATE_TODAY}]]"
modified: "[[{DATE_TODAY}]]"
template: "[[template-state-board-of-education]]"
name: "[[{state_name}]]"
{url_line}
state: "{abbreviation}"
tags: 
- "#organization"
- "#organization/state-board-of-education"
---

# {state_name}
"""
    return content

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    try:
        with open(INPUT_CSV, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

            count = 0
            for row in reader:
                state = row['state'].strip()
                abbreviation = row['abbreviation'].strip()
                url = row['boe_url'].strip()
                
                if not state:
                    continue

                filename = f"{create_slug(state)}-state-board-of-education.md"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                content = generate_markdown(state, abbreviation, url)
                
                with open(filepath, 'w', encoding='utf-8') as mdfile:
                    mdfile.write(content)
                
                count += 1
            
            print(f"Successfully created {count} markdown files in '{OUTPUT_DIR}'.")

    except FileNotFoundError:
        print(f"Error: Could not find input file '{INPUT_CSV}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
