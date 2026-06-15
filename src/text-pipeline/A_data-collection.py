import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from playwright.sync_api import sync_playwright

def download_fed_transcripts():

    print(f"\n== Collecting the data from the Fed... ==")

    output_dir = "data/transcripts/Fed/"
    os.makedirs(output_dir, exist_ok=True)
    
    base_url = "https://www.federalreserve.gov"
    main_calendar_url = f"{base_url}/monetarypolicy/fomccalendars.htm"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    calendar_pages = [main_calendar_url]
    for year in range(2015, 2027): 
        calendar_pages.append(f"{base_url}/monetarypolicy/fomchistorical{year}.htm")
    
    pages_to_scan = list(calendar_pages) 
    
    for cal_url in calendar_pages:
        try:
            response = session.get(cal_url, timeout=10)
            if response.status_code == 404:
                continue # Skip future years that don't exist yet
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'presconf' in href.lower() and '.htm' in href.lower():
                    full_media_url = urljoin(base_url, href)
                    if full_media_url not in pages_to_scan:
                        pages_to_scan.append(full_media_url)
                        
        except requests.exceptions.RequestException as e:
            continue

    downloaded_files = set(os.listdir(output_dir))
    if downloaded_files:
        True

    new_downloads_count = 0

    for page_url in pages_to_scan:
        try:
            response = session.get(page_url, timeout=10)
            if response.status_code == 404:
                continue
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
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
                
                if filename in downloaded_files:
                    continue
                
                file_path = os.path.join(output_dir, filename)
                
                try:
                    pdf_response = session.get(full_url, timeout=10)
                    pdf_response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        f.write(pdf_response.content)
                        
                    downloaded_files.add(filename)
                    new_downloads_count += 1
                except requests.exceptions.RequestException as e:
                    continue

                time.sleep(1)

    print(f"\nSuccess! Downloaded {new_downloads_count} new transcripts. Your '{output_dir}' directory now has a total of {len(downloaded_files)} files.")


def download_ecb_transcripts():
    print(f"\n== Collecting the data from the ECB... ==")

    output_dir = "data/transcripts/ECB/"
    os.makedirs(output_dir, exist_ok=True)
    
    base_url = "https://www.ecb.europa.eu"
    index_url = f"{base_url}/press/press_conference/monetary-policy-statement/html/index.en.html"

    downloaded_files = set(os.listdir(output_dir))
    if downloaded_files:
        True

    new_downloads_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(index_url, timeout=30000)
            page.wait_for_selector('a.arrow[lang="en"]', timeout=15000)
            last_height = page.evaluate("document.body.scrollHeight")
            
            while True:
                for _ in range(8): 
                    page.evaluate("window.scrollBy(0, 1000);")
                    page.wait_for_timeout(300) 
                
                page.wait_for_timeout(2000) 
                
                new_height = page.evaluate("document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                    
                last_height = new_height

        except Exception as e:
            browser.close()
            return

        soup = BeautifulSoup(page.content(), 'html.parser')
        
        target_links = soup.find_all('a', class_='arrow', lang='en')
        
        for link in target_links:
            href = link.get('href')
            
            if not href or '/monetary-policy-statement/' not in href:
                continue
                
            full_url = urljoin(base_url, href)
            filename = full_url.split('/')[-1].replace('.html', '.txt')
            
            if filename in downloaded_files:
                continue
                
            file_path = os.path.join(output_dir, filename)
            
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
                    continue                    
            except Exception as e:
                continue

        browser.close()

    print(f"\nSuccess! Extracted {new_downloads_count} new ECB transcripts. Your '{output_dir}' directory now has a total of {len(downloaded_files)} files.")


def download_boe_transcripts():
    print(f"\n== Collecting the data from the BoE... ==")

    output_dir = "data/transcripts/BoE/"
    os.makedirs(output_dir, exist_ok=True)
    
    base_url = "https://www.bankofengland.co.uk"
    months = ["february", "may", "august", "november"]
    pages_to_scan = []
    
    for year in range(2000, 2027): 
        for month in months:
            pages_to_scan.append(f"{base_url}/monetary-policy-report/{year}/{month}-{year}")
            pages_to_scan.append(f"{base_url}/inflation-report/{year}/{month}-{year}")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    downloaded_files = set(os.listdir(output_dir))
    if downloaded_files:
        True

    new_downloads_count = 0

    for page_url in pages_to_scan:
        try:
            response = session.get(page_url, timeout=10)
            if response.status_code == 404:
                continue
            response.raise_for_status()
        except requests.exceptions.RequestException:
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True).lower()
            is_pdf = '.pdf' in href.lower()
            
            keywords = ['transcript', 'remarks', 'statement', 'press-conference']
            is_target = any(kw in link_text or kw in href.lower() for kw in keywords)
            
            if is_pdf and is_target:
                full_url = urljoin(base_url, href)
                filename = full_url.split('/')[-1].split('?')[0]
                
                if filename in downloaded_files:
                    continue
                    
                file_path = os.path.join(output_dir, filename)
                
                try:
                    pdf_response = session.get(full_url, timeout=15)
                    pdf_response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        f.write(pdf_response.content)
                        
                    downloaded_files.add(filename)
                    new_downloads_count += 1
                except requests.exceptions.RequestException as e:
                    continue                
                time.sleep(1)

    # 2020 releases that used one-off URL structures (joint MPR+FSR and emergency meetings)
    hardcoded_pdfs = [
        "https://www.bankofengland.co.uk/-/media/boe/files/news/2020/march/interest-rate-cut-11-march-2020-transcript.pdf",
        "https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2020/may/mpr-fsr-press-conference-transcript-may-2020.pdf",
        "https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2020/august/mpr-fsr-press-conference-transcript-august-2020.pdf",
    ]
    for full_url in hardcoded_pdfs:
        filename = full_url.split('/')[-1]
        if filename not in downloaded_files:
            try:
                pdf_response = session.get(full_url, timeout=15)
                pdf_response.raise_for_status()
                with open(os.path.join(output_dir, filename), 'wb') as f:
                    f.write(pdf_response.content)
                downloaded_files.add(filename)
                new_downloads_count += 1
                print(f"  [hardcoded] Downloaded {filename}")
            except requests.exceptions.RequestException as e:
                print(f"  [hardcoded] FAILED {filename}: {e}")

    print(f"\nSuccess! Downloaded {new_downloads_count} new BoE documents. Your '{output_dir}' directory now has a total of {len(downloaded_files)} files.")


if __name__ == "__main__":
    download_fed_transcripts()
    download_ecb_transcripts()
    download_boe_transcripts()
