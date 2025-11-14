#!/usr/bin/env python
"""
Enhanced parser for SFR.GOV.RU with hierarchical structure extraction
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import json

class SFRParser:
    def __init__(self):
        self.base_url = "https://sfr.gov.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def parse_main_page(self, url):
        """Parse main category page and extract sublinks"""
        print(f"Parsing: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract main title
            main_title = soup.find('h1', class_='re-container__head-title')
            main_title_text = main_title.get_text(strip=True) if main_title else "No title found"
            
            print(f"Main title: {main_title_text}")
            
            # Find the link list container
            link_container = soup.find('div', class_=re.compile(r're-container__link-list'))
            sublinks = []
            
            if link_container:
                # Extract all links from the container
                links = link_container.find_all('a', href=True)
                for link in links:
                    sublinks.append({
                        'title': link.get_text(strip=True),
                        'url': urljoin(self.base_url, link['href']),
                        'full_url': urljoin(self.base_url, link['href'])
                    })
            
            print(f"Found {len(sublinks)} sublinks")
            return {
                'main_title': main_title_text,
                'main_url': url,
                'sublinks': sublinks
            }
            
        except Exception as e:
            print(f"Error parsing main page: {str(e)}")
            return None

    def parse_subpage(self, url):
        """Parse individual subpage and extract content"""
        print(f"  Parsing subpage: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract page title
            title = soup.find('h1', class_='re-container__head-title')
            title_text = title.get_text(strip=True) if title else "No title"
            
            # Extract main content
            content_div = soup.find('div', class_='re-container__inner-left')
            content_text = ""
            sub_sublinks = []
            
            if content_div:
                # Extract text content
                paragraphs = content_div.find_all(['p', 'li'])
                content_parts = []
                
                for element in paragraphs:
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:  # Filter out very short texts
                        content_parts.append(text)
                
                content_text = "\n".join(content_parts)
                
                # Extract sub-sublinks from content
                content_links = content_div.find_all('a', href=True)
                for link in content_links:
                    link_text = link.get_text(strip=True)
                    if link_text:  # Only include links with text
                        sub_sublinks.append({
                            'title': link_text,
                            'url': urljoin(self.base_url, link['href'])
                        })
            
            return {
                'title': title_text,
                'url': url,
                'content': content_text,
                'sub_sublinks': sub_sublinks
            }
            
        except Exception as e:
            print(f"  Error parsing subpage: {str(e)}")
            return None

    def parse_category_hierarchy(self, main_url):
        """Parse entire category hierarchy"""
        print(f"\n{'='*80}")
        print(f"Parsing category: {main_url}")
        print('='*80)
        
        # Parse main page
        main_data = self.parse_main_page(main_url)
        if not main_data:
            return None
        
        result = {
            'category_title': main_data['main_title'],
            'category_url': main_data['main_url'],
            'subpages': []
        }
        
        # Parse each subpage
        for i, sublink in enumerate(main_data['sublinks'], 1):
            print(f"[{i}/{len(main_data['sublinks'])}] Processing: {sublink['title']}")
            
            subpage_data = self.parse_subpage(sublink['url'])
            if subpage_data:
                result['subpages'].append(subpage_data)
            
            # Small delay to be respectful to the server
            import time
            time.sleep(1)
        
        return result

    def save_results(self, data, filename):
        """Save parsed data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Results saved to {filename}")

def main():
    parser = SFRParser()
    
    test_urls = [
        'https://sfr.gov.ru/grazhdanam/pensionres/',
        'https://sfr.gov.ru/grazhdanam/semyam_s_detmi/',
        'https://sfr.gov.ru/grazhdanam/invalidam/',
    ]
    
    print("SFR.GOV.RU HIERARCHICAL PARSER")
    print("="*80)
    
    for url in test_urls:
        category_data = parser.parse_category_hierarchy(url)
        
        if category_data:
            # Generate filename from category title
            filename = f"sfr_{category_data['category_title'].replace(' ', '_').lower()}.json"
            parser.save_results(category_data, filename)
            
            # Print summary
            print(f"\nSummary for '{category_data['category_title']}':")
            print(f"  - Main URL: {category_data['category_url']}")
            print(f"  - Subpages parsed: {len(category_data['subpages'])}")
            
            total_sub_sublinks = sum(len(page['sub_sublinks']) for page in category_data['subpages'])
            print(f"  - Total sub-sublinks found: {total_sub_sublinks}")
            
            # Print first subpage as example
            if category_data['subpages']:
                first_page = category_data['subpages'][0]
                print(f"\n  Example subpage:")
                print(f"    Title: {first_page['title']}")
                print(f"    Content preview: {first_page['content'][:100]}...")
                print(f"    Sub-sublinks: {len(first_page['sub_sublinks'])}")
        
        print("\n" + "-"*80 + "\n")

if __name__ == '__main__':
    main()