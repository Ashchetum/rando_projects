import csv
import sys
import subprocess
import time
from datetime import datetime

# ==========================================
# CONFIGURABLE VARIABLES
# ==========================================
CSV_FILE_PATH = "routes_small.csv" 
DELAY_SECONDS = 5  # Keeping your 5-second pacing
# ==========================================

def ensure_playwright_browsers():
    """Ensures the headless browser binaries and system libraries are installed."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("📦 Installing playwright library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "beautifulsoup4"])
    
    print("🤖 Checking browser binaries...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    print("⚙️ Checking system dependencies...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install-deps"])

def run_diagnostic_test():
    ensure_playwright_browsers()
    
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup

    stats_urls = []
    
    print(f"\n📂 Reading routes from {CSV_FILE_PATH}...")
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header row
            for row in reader:
                if len(row) > 2:
                    url = row[2].strip()
                    if "mountainproject.com/route/" in url:
                        stats_url = url.replace("mountainproject.com/route/", "mountainproject.com/route/stats/")
                        stats_urls.append(stats_url)
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return

    total_routes = len(stats_urls)
    print(f"📋 Loaded {total_routes} routes for the diagnostic test.")
    
    with sync_playwright() as p:
        print("🚀 Launching headless browser...")
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for idx, url in enumerate(stats_urls, 1):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Testing Route [{idx}/{total_routes}]: {url}")
            
            try:
                page.goto(url, wait_until="load")
                
                # Wait for the front-end frame to load
                page.wait_for_selector(".onx-stats-table", timeout=8000)
                time.sleep(1.0) # Generous wait to let data bind to the table rows
                
                rendered_html = page.content()
                
            except Exception as e:
                print(f"  ❌ Browser layout error: {e}")
                continue

            soup = BeautifulSoup(rendered_html, 'html.parser')
            
            # Use a slightly wider selection strategy to capture the rows
            tick_rows = soup.select('tr[id^="ticks."]')
            if not tick_rows:
                tick_rows = soup.select('.onx-stats-table table tr')
            if not tick_rows:
                tick_rows = soup.select('.onx-stats-table tr')

            # Test execution block: Did we find any rows at all?
            if not tick_rows:
                print("  ❌ DIAGNOSTIC FAILED: No HTML rows found inside the selector module.")
                print("     (This means the page is still loading empty for Python, or the selector changed)")
                continue
            
            # Grab just the absolute first row to check its inner content
            first_row = tick_rows[0]
            raw_text = first_row.get_text(separator=' | ', strip=True)
            
            print("  🔍 DIAGNOSTIC SUCCESS! Raw text read from Tick #1:")
            print(f"     ↳ \"{raw_text}\"")

            if idx < total_routes:
                time.sleep(DELAY_SECONDS)

        context.close()
        browser.close()

if __name__ == "__main__":
    run_diagnostic_test()