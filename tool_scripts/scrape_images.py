import csv
import time
import random
import requests
from bs4 import BeautifulSoup
import lxml.html
import json
import re

def get_image_url(url):
    try:
        print(f"Processing: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://reverb.com/',
            'DNT': '1'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Try to find image URL in the page's metadata
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Method 1: Look for the image in the header section
        header_image = soup.select_one('.csp2-header__image img')
        if header_image and header_image.get('src'):
            print(f"Found image in header: {header_image['src']}")
            return header_image['src']
        
        # Method 2: Look for og:image meta tag
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            print(f"Found image in og:image: {og_image['content']}")
            return og_image['content']
        
        # Method 3: Look for JSON-LD data
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'image' in data:
                    print(f"Found image in JSON-LD: {data['image']}")
                    return data['image']
            except json.JSONDecodeError:
                pass
        
        # Method 4: Look for image in the page's JSON data
        json_data = soup.find('script', string=re.compile(r'window\.__INITIAL_STATE__'))
        if json_data:
            try:
                # Extract the JSON data from the script tag
                json_str = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', json_data.string, re.DOTALL)
                if json_str:
                    data = json.loads(json_str.group(1))
                    # Navigate through the JSON structure to find the image URL
                    if 'entities' in data and 'products' in data['entities']:
                        for product in data['entities']['products'].values():
                            if 'photos' in product and product['photos']:
                                image_url = product['photos'][0].get('_links', {}).get('large_crop', {}).get('href')
                                if image_url:
                                    print(f"Found image in page JSON: {image_url}")
                                    return image_url
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # Method 5: Try to find any image in the product section
        product_image = soup.select_one('.rc-image img')
        if product_image and product_image.get('src'):
            print(f"Found image in product section: {product_image['src']}")
            return product_image['src']
        
        print(f"No image found for {url}")
        return None
            
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def main():
    # Read the existing CSV
    rows = []
    with open('database.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Get the header row
        
        # Check if image_url column exists
        has_image_column = 'image_url' in header
        if not has_image_column:
            header.append('image_url')
        
        rows.append(header)
        
        # Process each row
        for row in reader:
            # Pad row to at least 5 columns
            while len(row) < 5:
                row.append('')
            
            # Only scrape if image_url is missing or empty
            image_url = row[4].strip() if len(row) > 4 else ''
            if image_url:
                # Already has an image URL, just keep the row
                rows.append(row)
                continue
            
            link = row[3].strip() if len(row) > 3 else ''
            if not link:
                # No link to scrape from, just keep the row
                rows.append(row)
                continue
            
            # Get the image URL
            scraped_url = get_image_url(link)
            row[4] = scraped_url if scraped_url else ''
            rows.append(row)
            
            # Add a delay to be nice to Reverb's servers
            delay = random.uniform(2, 3)
            print(f"Waiting {delay:.1f} seconds...")
            time.sleep(delay)
    
    # Write the updated data back to the CSV
    with open('database.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    
    print("Scraping complete! Results saved to database.csv")

if __name__ == "__main__":
    main() 