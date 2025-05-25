import requests
from bs4 import BeautifulSoup
import csv

def scrape_specific_content(url, tag, class_name=None, id_name=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    if class_name:
        elements = soup.find_all(tag, class_=class_name)
    elif id_name:
        elements = soup.find_all(tag, id=id_name)
    else:
        elements = soup.find_all(tag)
    results = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
    return results

if __name__ == "__main__":
    url = input("Enter the URL to scrape: ")
    tag = input("Enter the HTML tag to target (e.g., h1, h2, h3): ")
    class_name = input("Enter the class name to filter (leave blank if none): ") or None
    id_name = input("Enter the id name to filter (leave blank if none): ") or None

    content = scrape_specific_content(url, tag, class_name, id_name)
    print("Content found:")
    for idx, item in enumerate(content, 1):
        print(f"{idx}. {item}")

    # Save to CSV
    with open("scraped_content.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Content"])
        for item in content:
            writer.writerow([item])
    print("Content saved to scraped_content.csv")