import requests
from bs4 import BeautifulSoup

# Generate URLs from page 1 to 8
base_url = "https://www.mountainproject.com/forum/103989416/for-sale-for-free-want-to-buy?page="
urls = [f"{base_url}{i}" for i in range(1, 9)]

# Strings to search for
search_terms = ["brass", "nut", "stop"]

# Headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Crawl and search
for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        lines = soup.get_text().splitlines()

        for line in lines:
            lower_line = line.lower()
            for term in search_terms:
                if term in lower_line:
                    print(f"\nFound '{term}' on: \033[94m{url}\033[0m")
                    print(f"  Line: {line.strip()}")
    except Exception as e:
        print(f"Error processing {url}: {e}")