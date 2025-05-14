import csv
import os
import requests
import time
import random
from urllib.parse import urlparse
from pathlib import Path

def download_image(url, filename):
    try:
        # Clean up the URL by removing any extra characters or spaces
        url = url.strip('[]\'"')
        
        # If the URL contains multiple URLs (comma-separated), take the last one
        if ',' in url:
            url = url.split(',')[-1].strip()
        
        # If the URL is a partial Reverb image URL, add the base domain
        if url.startswith('w_') or url.startswith('a_') or url.startswith('c_'):
            url = f"https://rvb-img.reverb.com/image/upload/{url}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://reverb.com/',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def parseCSVRow(row):
    try:
        # Convert row to string if it's a list
        if isinstance(row, list):
            row = ','.join(row)
        
        parts = []
        currentPart = ''
        inBrackets = False
        
        for char in row:
            if char == '[':
                inBrackets = True
                currentPart += char
            elif char == ']':
                inBrackets = False
                currentPart += char
            elif char == ',' and not inBrackets:
                parts.append(currentPart.strip())
                currentPart = ''
            else:
                currentPart += char
        
        if currentPart:
            parts.append(currentPart.strip())
        
        # If we have more than 5 parts, the image URL was split
        if len(parts) > 5:
            # First 4 parts are correct (brand, model, type, link)
            # Combine the rest into the image URL
            image_url = ','.join(parts[4:])
            # Clean up the image URL
            image_url = image_url.strip('[]\'"')
            parts = parts[:4] + [image_url]
        
        # Handle cases where we have 4 parts by adding an empty image URL
        if len(parts) == 4:
            parts.append('')
            
        if len(parts) != 5:
            print(f"Warning: Row has {len(parts)} parts, expected 5. Parts: {parts}")
            return None
            
        # Clean up the image URL if it exists
        if parts[4]:
            parts[4] = parts[4].strip('[]\'"')
            
        return parts
    except Exception as e:
        print(f"Error parsing row: {str(e)}")
        print(f"Problematic row: {row}")
        return None

def main():
    # Create images directory if it doesn't exist
    images_dir = Path('images')
    images_dir.mkdir(exist_ok=True)
    
    # Read the CSV file
    with open('database.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip header row
        
        # Process each row
        for row_num, row in enumerate(reader, start=2):  # start=2 because we skipped header
            try:
                # Parse the row
                parts = parseCSVRow(row)
                if not parts:
                    print(f"Skipping row {row_num} due to parsing error")
                    continue
                
                brand, model, pedal_type, link, image_url = parts  # renamed 'type' to 'pedal_type'
                
                if not image_url:
                    print(f"No image URL for {brand} {model} (row {row_num})")
                    continue
                
                # Create a safe filename from brand and model
                safe_brand = "".join(c for c in brand if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_model = "".join(c for c in model if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"{safe_brand}_{safe_model}.jpg"
                filepath = images_dir / filename
                
                # Skip if image already exists
                if filepath.exists():
                    # print(f"Image already exists: {filename}")
                    continue
                
                print(f"Downloading {brand} {model} (row {row_num})...")
                if download_image(image_url, filepath):
                    print(f"Successfully downloaded: {filename}")
                else:
                    print(f"Failed to download: {filename}")
                
                # Add a 2.5 second delay between downloads
                time.sleep(2.5)
                
            except Exception as e:
                print(f"Error processing row {row_num}:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Row data: {row}")
                continue

if __name__ == "__main__":
    main() 