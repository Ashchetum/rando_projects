import csv
import sys
import subprocess
import time
import re
import os
from datetime import datetime

# ==========================================
# CONFIGURABLE VARIABLES
# ==========================================
INPUT_CSV_PATH = "routes_small.csv" 
OUTPUT_CSV_PATH = "booty_finder_results.csv"

TICKS_TO_CHECK = 5
DELAY_SECONDS = 60  # this is the robot.txt guidline :) 

KEYWORDS = [
    r"\bbail(ed|ing)?\b", 
    r"\bleft\b.*\b(gear|cam|nut|draw|rope|biner|rack)\b", 
    r"\bfixed\b.*\b(gear|piece|pro|pin|boot)\b", 
    r"\bbooty\b",
    r"\babandon(ed)?\b"
]
# ==========================================


# Set up runtime environment for codespace
def ensure_playwright_browsers():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("📦 Installing playwright library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "beautifulsoup4"])
    
    print("🤖 Verifying browser binaries...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    print("⚙️ Verifying system dependencies...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install-deps"])


def run_production_scanner():
    ensure_playwright_browsers()
    
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup

    keyword_regex = re.compile("|".join(KEYWORDS), re.IGNORECASE)
    routes_to_scan = []
    
    # Step 1: Ingest the input file
    print(f"\n📂 Reading target routes from {INPUT_CSV_PATH}...")
    try:
        with open(INPUT_CSV_PATH, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Extract header row
            
            for row in reader:
                if len(row) > 2:
                    route_name = row[0].strip() if len(row) > 0 else "Unknown Route"
                    raw_url = row[2].strip()
                    if "mountainproject.com/route/" in raw_url:
                        stats_url = raw_url.replace("mountainproject.com/route/", "mountainproject.com/route/stats/")
                        routes_to_scan.append({
                            'name': route_name,
                            'original_url': raw_url,
                            'stats_url': stats_url
                        })
    except Exception as e:
        print(f"❌ Error reading input CSV file: {e}")
        return

    total_routes = len(routes_to_scan)
    print(f"📋 Loaded {total_routes} routes for deep text parsing.")
    
    # Step 2: Initialize a brand new, timestamped output CSV file
    # Generates a string like "20260626_1600" based on the current time
    time_stamp = datetime.now().strftime("%Y%m%d_%H%M")
    OUTPUT_CSV_PATH = f"booty_finder_{time_stamp}.csv"
    
    print(f"✨ Creating fresh output log: {OUTPUT_CSV_PATH}")
    try:
        with open(OUTPUT_CSV_PATH, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp Found", "Route Name", "Route URL", "Matching Tick Text"])
    except Exception as e:
        print(f"❌ Cannot create output file: {e}")
        return

    # Step 3: Run the browser processing engine
    with sync_playwright() as p:
        print("🚀 Launching background processing engine...")
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for idx, route in enumerate(routes_to_scan, 1):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Processing [{idx}/{total_routes}]: {route['name']}")
            
            try:
                page.goto(route['stats_url'], wait_until="load")
                page.wait_for_selector(".onx-stats-table", timeout=8000)
                time.sleep(0.5) 
                
                rendered_html = page.content()
            except Exception as e:
                print(f"  ❌ Layout timeout/error on: {route['name']}")
                continue

            soup = BeautifulSoup(rendered_html, 'html.parser')
            tick_rows = soup.select('tr[id^="ticks."]')
            if not tick_rows:
                tick_rows = soup.select('.onx-stats-table table tr')

            if not tick_rows:
                continue

            recent_ticks = tick_rows[:TICKS_TO_CHECK]
            
            for row in recent_ticks:
                text_content = row.get_text(separator=' | ', strip=True)
                
                if keyword_regex.search(text_content):
                    print(f"  🚨 MATCH FOUND on {route['name']}! Logging to file...")
                    
                    # On-the-fly incremental write block
                    with open(OUTPUT_CSV_PATH, mode='a', newline='', encoding='utf-8') as out_f:
                        writer = csv.writer(out_f)
                        writer.writerow([timestamp, route['name'], route['original_url'], text_content])

            if idx < total_routes:
                time.sleep(DELAY_SECONDS)

        context.close()
        browser.close()

    print(f"\n🏁 Scan complete!: {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    run_production_scanner()