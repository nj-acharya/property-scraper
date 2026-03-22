import cloudscraper
import re
import csv
from datetime import datetime

def get_redfin_data(url):
    # Use a specific browser fingerprint to look as human as possible
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    try:
        print(f"Accessing Redfin...")
        response = scraper.get(url)
        # We treat the entire page as a single string of text
        html_text = response.text
        # print(html_text)

        # 1. Redfin Estimate ($2,019,986)
        # We look for the dollar amount that appears immediately BEFORE the 'Est. refi payment' label
        estimate = "Not Found"
        est_match = re.search(r'(\$[\d,]+)\s*Est\. refi payment', html_text)
        if est_match:
            estimate = est_match.group(1)
        else:
            # Backup: find the bold price in the Redfin Estimate section
            backup_est = re.search(r'Redfin Estimate.*?(\$[\d,]+)', html_text, re.DOTALL)
            if backup_est:
                estimate = backup_est.group(1)

        # 2. Sale Range ($1.92M – $2.32M)
        price_range = "Not Found"
        range_match = re.search(r'\$[\d\.]+M\s*', html_text)
        if range_match:
            price_range = range_match.group(0)

        # 3. Rental Estimate ($5,596)
        rental_est = "Not Found"
        # We look for the encoded path and then the predictedValue immediately following it
        rental_pattern = r'rental-estimate.*?predictedValue":\s*(\d+)'
        rental_match = re.search(rental_pattern, html_text, re.DOTALL)
        
        if rental_match:
            rental_est = f"${int(rental_match.group(1)):,}"
        else:
            # Fallback for the specific encoding \u002F seen in your HTML
            rental_fallback = re.search(r'rental-estimate.*?predictedValue\\":(\d+)', html_text)
            if rental_fallback:
                rental_est = f"${int(rental_fallback.group(1)):,}"

        return {
            "Address": "1147 California St",
            "Redfin Estimate": estimate,
            "Low end of Range": price_range,
            "Rental Estimate": rental_est
        }

    except Exception as e:
        return f"Bot Error: {str(e)}"

# Execute
url = "https://www.redfin.com/CA/Mountain-View/1147-California-St-94041/home/1113904"
data = get_redfin_data(url)

print("\n--- Property Stats for 1147 California St ---")
for key, val in data.items():
    print(f"{key}: {val}")

if isinstance(data, dict):
    file_path = "property_history.csv"
    file_exists = False
    try:
        with open(file_path, 'r') as f: file_exists = True
    except FileNotFoundError: pass

    with open(file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    
    print(f"\n--- Data Logged Successfully to {file_path} ---")
    for key, val in data.items():
        print(f"{key}: {val}")
else:
    print(data)