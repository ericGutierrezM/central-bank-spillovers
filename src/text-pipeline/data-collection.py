import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from playwright.sync_api import sync_playwright

def download_fed_transcripts():
    output_dir = "data/transcripts/Fed/"
    os.makedirs(output_dir, exist_ok=True)
    
    base_url = "https://www.federalreserve.gov"
    main_calendar_url = f"{base_url}/monetarypolicy/fomccalendars.htm"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    # 1. Build a comprehensive list of BASE calendar pages
    calendar_pages = [main_calendar_url]
    for year in range(2015, 2027): 
        calendar_pages.append(f"{base_url}/monetarypolicy/fomchistorical{year}.htm")

    # 2. Pre-scan ALL calendar pages for intermediate "Press Conference" HTML pages
    print(f"Pre-scanning all calendar pages for intermediate media pages...")
    
    # We will eventually scan all base calendars PLUS any intermediate pages we find
    pages_to_scan = list(calendar_pages) 
    
    for cal_url in calendar_pages:
        try:
            response = session.get(cal_url, timeout=10)
            if response.status_code == 404:
                continue # Skip future years that don't exist yet
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the intermediate links you discovered
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'presconf' in href.lower() and '.htm' in href.lower():
                    full_media_url = urljoin(base_url, href)
                    if full_media_url not in pages_to_scan:
                        pages_to_scan.append(full_media_url)
                        print(f"  [+] Found intermediate page: {full_media_url}")
                        
        except requests.exceptions.RequestException as e:
            print(f"[-] Failed to pre-scan {cal_url}: {e}")

    # ==========================================
    # NEW: Local File Detection
    # ==========================================
    # Read the directory to see what is already downloaded
    downloaded_files = set(os.listdir(output_dir))
    if downloaded_files:
        print(f"\n[*] Found {len(downloaded_files)} existing files in '{output_dir}'. These will be skipped to save runtime.")

    new_downloads_count = 0

    # 3. Now scan all collected pages for the actual PDF links
    for page_url in pages_to_scan:
        print(f"\nScanning: {page_url}")
        try:
            response = session.get(page_url, timeout=10)
            if response.status_code == 404:
                print("  [-] Page not found (Expected for future/unreleased historical years)")
                continue
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"  [-] Failed to access {page_url}: {e}")
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True).lower()
            
            is_historical = 'presconf' in link_text and '.pdf' in href.lower()
            is_recent = 'presconf' in href.lower() and '.pdf' in href.lower()
            
            if is_historical or is_recent:
                full_url = urljoin(base_url, href)
                filename = full_url.split('/')[-1].split('?')[0]
                
                # Check if the file is already in our local set
                if filename in downloaded_files:
                    # Optional: Print a message showing it was skipped (commented out to reduce console spam)
                    # print(f"  [~] Skipping {filename} (Already exists)")
                    continue
                
                file_path = os.path.join(output_dir, filename)
                print(f"  [+] Found NEW PDF -> Downloading {filename}...")
                
                try:
                    pdf_response = session.get(full_url, timeout=10)
                    pdf_response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        f.write(pdf_response.content)
                        
                    downloaded_files.add(filename)
                    new_downloads_count += 1
                except requests.exceptions.RequestException as e:
                    print(f"  [-] Failed to download {filename}: {e}")
                
                time.sleep(1)

    print(f"\nSuccess! Downloaded {new_downloads_count} new transcripts. Your '{output_dir}' directory now has a total of {len(downloaded_files)} files.")


def download_ecb_transcripts():
    output_dir = "data/transcripts/ECB/"
    os.makedirs(output_dir, exist_ok=True)
    
    base_url = "https://www.ecb.europa.eu"
    index_url = f"{base_url}/press/press_conference/monetary-policy-statement/html/index.en.html"

    downloaded_files = set(os.listdir(output_dir))
    if downloaded_files:
        print(f"\n[*] Found {len(downloaded_files)} existing files in '{output_dir}'. These will be skipped.")

    new_downloads_count = 0

    print(f"\nStarting Playwright to load ECB Index...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(index_url, timeout=30000)
            print("  Waiting for initial links to appear...")
            page.wait_for_selector('a.arrow[lang="en"]', timeout=15000)
            
            # ==========================================
            # THE FIX: Progressive "Human-Like" Scroll
            # ==========================================
            print("  Scrolling progressively to trigger ALL lazy-loaded batches...")
            last_height = page.evaluate("document.body.scrollHeight")
            
            while True:
                # Scroll down in smaller increments rather than one massive jump
                for _ in range(8): 
                    page.evaluate("window.scrollBy(0, 1000);")
                    # Wait a tiny bit between mouse-wheel scrolls
                    page.wait_for_timeout(300) 
                
                # Wait for the ECB servers to process and inject the new middle links
                page.wait_for_timeout(2000) 
                
                new_height = page.evaluate("document.body.scrollHeight")
                
                if new_height == last_height:
                    print("  [+] Reached the absolute end of the archives.")
                    break
                    
                last_height = new_height
                print("  [*] Triggered a middle batch, continuing scroll...")
            # ==========================================

        except Exception as e:
            print(f"[-] Failed to load page or scroll. Error: {e}")
            browser.close()
            return

        # Now grab the completely filled out HTML
        soup = BeautifulSoup(page.content(), 'html.parser')
        
        target_links = soup.find_all('a', class_='arrow', lang='en')
        print(f"\n  [+] JavaScript finished! Found {len(target_links)} English transcript links.\n")
        
        for link in target_links:
            href = link.get('href')
            
            if not href or '/monetary-policy-statement/' not in href:
                continue
                
            full_url = urljoin(base_url, href)
            filename = full_url.split('/')[-1].replace('.html', '.txt')
            
            if filename in downloaded_files:
                continue
                
            file_path = os.path.join(output_dir, filename)
            print(f"  [+] Extracting text to {filename}...")
            
            try:
                page.goto(full_url, timeout=15000)
                page.wait_for_load_state("domcontentloaded")
                transcript_soup = BeautifulSoup(page.content(), 'html.parser')
                
                main_content = transcript_soup.find('main') or transcript_soup
                paragraphs = main_content.find_all(['p', 'h2', 'h3'])
                text_content = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                
                if len(text_content.strip()) > 100:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                        
                    downloaded_files.add(filename)
                    new_downloads_count += 1
                else:
                    print(f"  [-] Extracted text for {filename} was suspiciously short. Skipping.")
                    
            except Exception as e:
                print(f"  [-] Failed to extract {filename}: {e}")
        
        browser.close()

    print(f"\nSuccess! Extracted {new_downloads_count} new ECB transcripts. Your '{output_dir}' directory now has a total of {len(downloaded_files)} files.")


def download_boe_transcripts():
    output_dir = "data/transcripts/BoE/"
    os.makedirs(output_dir, exist_ok=True)
    
    base_url = "https://www.bankofengland.co.uk"
    months = ["february", "may", "august", "november"]
    pages_to_scan = []
    
    # 1. Extended timeline: Generate URLs back to the year 2000
    for year in range(2000, 2027): 
        for month in months:
            pages_to_scan.append(f"{base_url}/monetary-policy-report/{year}/{month}-{year}")
            pages_to_scan.append(f"{base_url}/inflation-report/{year}/{month}-{year}")

    # 2. Setup session and local file detection
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    downloaded_files = set(os.listdir(output_dir))
    if downloaded_files:
        print(f"\n[*] Found {len(downloaded_files)} existing files in '{output_dir}'. These will be skipped.")

    new_downloads_count = 0
    print("\nStarting BoE Download...")

    # 3. Scan the generated pages
    for page_url in pages_to_scan:
        try:
            response = session.get(page_url, timeout=10)
            if response.status_code == 404:
                continue
            response.raise_for_status()
        except requests.exceptions.RequestException:
            continue
            
        print(f"\nScanning: {page_url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 4. Find the Documents (Expanded Filter)
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True).lower()
            
            is_pdf = '.pdf' in href.lower()
            
            # --- THE FIX ---
            # Cast a wider net to catch both the Q&A transcripts AND the opening remarks/statements
            keywords = ['transcript', 'remarks', 'statement', 'press-conference']
            is_target = any(kw in link_text or kw in href.lower() for kw in keywords)
            
            if is_pdf and is_target:
                full_url = urljoin(base_url, href)
                filename = full_url.split('/')[-1].split('?')[0]
                
                if filename in downloaded_files:
                    continue
                    
                file_path = os.path.join(output_dir, filename)
                print(f"  [+] Found BoE Document -> Downloading {filename}...")
                
                try:
                    pdf_response = session.get(full_url, timeout=15)
                    pdf_response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        f.write(pdf_response.content)
                        
                    downloaded_files.add(filename)
                    new_downloads_count += 1
                except requests.exceptions.RequestException as e:
                    print(f"  [-] Failed to download {filename}: {e}")
                
                time.sleep(1)

    print(f"\nSuccess! Downloaded {new_downloads_count} new BoE documents. Your '{output_dir}' directory now has a total of {len(downloaded_files)} files.")


if __name__ == "__main__":
    download_fed_transcripts()
    #download_ecb_transcripts()
    #download_boe_transcripts()