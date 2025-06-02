#!/usr/bin/env python3
"""
Web Scraper for extracting article titles and links from blog pages.
This script demonstrates a modular approach to web scraping with error handling.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import sys
from typing import List, Dict, Optional


class WebScraper:
    """A modular web scraper for extracting article titles and links."""
    
    def __init__(self, base_url: str, timeout: int = 10, delay: float = 1.0):
        """
        Initialize the web scraper.
        
        Args:
            base_url: The base URL of the website to scrape
            timeout: Request timeout in seconds
            delay: Delay between requests to be respectful
        """
        self.base_url = base_url
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page.
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object if successful, None if failed
        """
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            
            # Raise an exception for bad status codes
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Add delay to be respectful to the server
            time.sleep(self.delay)
            
            return soup
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error parsing {url}: {e}")
            return None
    
    def extract_articles(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract article titles and links from the parsed HTML.
        
        Args:
            soup: BeautifulSoup object of the parsed page
            
        Returns:
            List of dictionaries containing article data
        """
        articles = []
        
        try:
            # Common selectors for article titles and links
            # Modify these selectors based on the target website's structure
            article_selectors = [
                'article h2 a',      # Articles with h2 titles
                'h1 a',              # H1 links
                'h2 a',              # H2 links  
                'h3 a',              # H3 links
                '.post-title a',     # WordPress-style post titles
                '.entry-title a',    # Another common WordPress class
                'a[href*="/blog/"]', # Links containing "/blog/"
                'a[href*="/post/"]', # Links containing "/post/"
                'a[href*="/article/"]' # Links containing "/article/"
            ]
            
            # Try each selector until we find articles
            for selector in article_selectors:
                links = soup.select(selector)
                if links:
                    print(f"Found {len(links)} articles using selector: {selector}")
                    break
            
            # If no specific selectors work, try finding all links with meaningful text
            if not links:
                print("Trying fallback: all links with substantial text")
                all_links = soup.find_all('a', href=True)
                links = [link for link in all_links if link.get_text(strip=True) 
                        and len(link.get_text(strip=True)) > 10]
            
            # Extract data from found links
            for link in links:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                if title and href:
                    # Convert relative URLs to absolute URLs
                    full_url = urljoin(self.base_url, href)
                    
                    # Skip invalid URLs or fragments
                    if self._is_valid_article_url(full_url):
                        articles.append({
                            'title': title,
                            'url': full_url
                        })
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_articles = []
            for article in articles:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    unique_articles.append(article)
            
            return unique_articles
            
        except Exception as e:
            print(f"Error extracting articles: {e}")
            return []
    
    def _is_valid_article_url(self, url: str) -> bool:
        """
        Check if a URL looks like a valid article URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if URL appears to be a valid article
        """
        try:
            parsed = urlparse(url)
            
            # Skip fragments, mailto, tel, etc.
            if not parsed.scheme.startswith('http'):
                return False
            
            # Skip common non-article paths
            skip_patterns = [
                '#', 'javascript:', 'mailto:', 'tel:',
                '/tag/', '/category/', '/author/', '/feed/',
                '.pdf', '.jpg', '.png', '.gif', '.css', '.js'
            ]
            
            return not any(pattern in url.lower() for pattern in skip_patterns)
            
        except Exception:
            return False
    
    def display_articles(self, articles: List[Dict[str, str]]) -> None:
        """
        Display the extracted articles in a formatted way.
        
        Args:
            articles: List of article dictionaries
        """
        if not articles:
            print("No articles found.")
            return
        
        print(f"\n{'='*60}")
        print(f"Found {len(articles)} articles:")
        print(f"{'='*60}")
        
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   URL: {article['url']}")
    
    def save_to_file(self, articles: List[Dict[str, str]], filename: str = "articles.txt") -> None:
        """
        Save articles to a text file.
        
        Args:
            articles: List of article dictionaries
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Scraped Articles - Total: {len(articles)}\n")
                f.write("="*60 + "\n\n")
                
                for i, article in enumerate(articles, 1):
                    f.write(f"{i}. {article['title']}\n")
                    f.write(f"   URL: {article['url']}\n\n")
            
            print(f"Articles saved to {filename}")
            
        except Exception as e:
            print(f"Error saving to file: {e}")


def main():
    """Main function to run the scraper."""
    
    # Configuration - Modify these variables for different websites
    TARGET_URL = input("Input the URL to scrape: ")  # Example blog URL
    OUTPUT_FILE = "scraped_articles.txt"
    
    # Alternative URLs to try:
    # TARGET_URL = "https://realpython.com/"
    # TARGET_URL = "https://www.hackerearth.com/blog/"
    # TARGET_URL = "https://medium.com/@python"
    
    print("Starting web scraper...")
    print(f"Target URL: {TARGET_URL}")
    
    # Initialize the scraper
    scraper = WebScraper(TARGET_URL, timeout=15, delay=1.0)
    
    # Fetch the main page
    soup = scraper.fetch_page(TARGET_URL)
    if not soup:
        print("Failed to fetch the main page. Exiting.")
        sys.exit(1)
    
    # Extract articles
    articles = scraper.extract_articles(soup)
    
    if articles:
        # Display results
        scraper.display_articles(articles)
        
        # Save to file
        scraper.save_to_file(articles, OUTPUT_FILE)
        
        print(f"\nScraping completed successfully!")
        print(f"Found {len(articles)} articles")
        print(f"Results saved to: {OUTPUT_FILE}")
    else:
        print("No articles were found. This might be due to:")
        print("- The website structure not matching our selectors")
        print("- The website blocking our requests")
        print("- Network issues")
        print("\nTry modifying the selectors in extract_articles() method")


if __name__ == "__main__":
    main()


# Example of how to modify for different data extraction:
# 
# For e-commerce product scraping, modify extract_articles() like this:
# 
# def extract_products(self, soup):
#     products = []
#     try:
#         # Product selectors (modify based on target site)
#         product_containers = soup.select('.product-item')  # Common class
#         
#         for container in product_containers:
#             name_elem = container.select_one('.product-name, h2, h3')
#             price_elem = container.select_one('.price, .product-price')
#             link_elem = container.select_one('a')
#             
#             if name_elem and price_elem:
#                 products.append({
#                     'name': name_elem.get_text(strip=True),
#                     'price': price_elem.get_text(strip=True),
#                     'url': urljoin(self.base_url, link_elem.get('href')) if link_elem else 'N/A'
#                 })
#         
#         return products
#     except Exception as e:
#         print(f"Error extracting products: {e}")
#         return []