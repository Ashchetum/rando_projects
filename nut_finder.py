import requests
from bs4 import BeautifulSoup

# Generate URLs from page 1 to 10
base_url = "https://www.mountainproject.com/forum/103989416/for-sale-for-free-want-to-buy?page="
urls = [f"{base_url}{i}" for i in range(1, 11)]

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

        # Find all hyperlinks on the page
        links = soup.find_all("a", href=True)

        for link in links:
            link_text = link.get_text().strip().lower()
            link_href = link["href"]

            for term in search_terms:
                if term in link_text:
                    print(f"\nFound '{term}':")
                    print(f"  Link Text: {link.get_text().strip()}")
                    print(f"  Hyperlink: \033[94m{link_href}\033[0m")
    except Exception as e:
        print(f"Error processing {url}: {e}")