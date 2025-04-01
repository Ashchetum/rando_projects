import requests
from bs4 import BeautifulSoup

# List of URLs to crawl
urls = [
    "https://example.com",
    "https://example.org",
    "https://example.net",
]

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
        page_text = soup.get_text().lower()

        for term in search_terms:
            if term in page_text:
                print(f"Found '{term}' on: {url}")
    except Exception as e:
        print(f"Error processing {url}: {e}")
