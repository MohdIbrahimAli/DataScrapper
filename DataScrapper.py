import requests
from bs4 import BeautifulSoup
import csv

def scrape_all_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = soup.stripped_strings
    return list(texts)

if __name__ == "__main__":
    url = input("Enter the URL to scrape: ")
    content = scrape_all_text(url)
    print("Content found:")
    for idx, item in enumerate(content, 1):
        print(f"{idx}. {item}")

    # Save to CSV with URL column
    with open("all_scraped_content.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Content"])
        for item in content:
            writer.writerow([url, item])
    print("Content saved to all_scraped_content.csv")
