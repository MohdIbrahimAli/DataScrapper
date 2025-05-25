import requests
from bs4 import BeautifulSoup

def scrape_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    # Try to find common article/title tags
    for tag in soup.find_all(['h1', 'h2', 'h3', 'article']):
        text = tag.get_text(strip=True)
        if text and len(text) > 10:  # Filter out very short headings
            articles.append(text)
    return articles

if __name__ == "__main__":
    url = input("Enter the URL to scrape: ")
    articles = scrape_articles(url)
    print("Articles/Topics found:")
    for idx, article in enumerate(articles, 1):
        print(f"{idx}. {article}")