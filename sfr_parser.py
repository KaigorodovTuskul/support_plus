#!/usr/bin/env python
"""
Enhanced SFR parser for multiple base URLs with timeout protection
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import pandas as pd
from collections import deque
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SFRRecursiveParser:
    def __init__(self):
        self.base_url = "https://sfr.gov.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Настройка сессии с повторными попытками
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Настройка retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.visited_urls = set()
        self.data_records = []
        self.current_id = 1
        self.failed_urls = []

    def safe_request(self, url, max_retries=3, timeout=30):
        """Безопасный запрос с повторными попытками и таймаутом"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                print(f"    Timeout attempt {attempt + 1}/{max_retries} for {url}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
                
            except requests.exceptions.ConnectionError as e:
                print(f"    Connection error attempt {attempt + 1}/{max_retries} for {url}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
                
            except requests.exceptions.RequestException as e:
                print(f"    Request error attempt {attempt + 1}/{max_retries} for {url}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
                
        return None

    def extract_links_from_page(self, url):
        """Extract all links from page that start with the given base URL but are not exactly the same"""
        try:
            response = self.safe_request(url)
            if not response:
                return set()
                
            soup = BeautifulSoup(response.content, 'lxml')
            
            all_links = soup.find_all('a', href=True)
            filtered_links = set()
            
            for link in all_links:
                href = link['href']
                full_url = urljoin(self.base_url, href)
                
                # Filter: links that start with the current URL but are not exactly the same
                if (full_url.startswith(url) and 
                    full_url != url and 
                    full_url not in self.visited_urls):
                    filtered_links.add(full_url)
            
            return filtered_links
            
        except Exception as e:
            print(f"Error extracting links from {url}: {str(e)}")
            self.failed_urls.append({'url': url, 'error': str(e), 'type': 'link_extraction'})
            return set()

    def extract_content(self, url):
        """Extract header and content from the page with error handling"""
        try:
            response = self.safe_request(url, timeout=45)
            if not response:
                return "Error: Request failed", ""
                
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract header
            header = soup.find('h1', class_='re-container__head-title')
            header_text = header.get_text(strip=True) if header else "No header"
            
            # Extract content from section-content div
            content_div = soup.find('div', class_=re.compile(r'section-content collapse show'))
            content_text = ""
            
            if content_div:
                # Extract all text content
                paragraphs = content_div.find_all(['p', 'li', 'div'])
                content_parts = []
                
                for element in paragraphs:
                    text = element.get_text(strip=True)
                    if text and len(text) > 5:
                        content_parts.append(text)
                
                content_text = "\n".join(content_parts)
            
            # If no content found in section-content, try other containers
            if not content_text:
                content_div = soup.find('div', class_='re-container__inner-left')
                if content_div:
                    paragraphs = content_div.find_all(['p', 'li'])
                    content_parts = []
                    
                    for element in paragraphs:
                        text = element.get_text(strip=True)
                        if text and len(text) > 5:
                            content_parts.append(text)
                    
                    content_text = "\n".join(content_parts)
            
            return header_text, content_text
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            self.failed_urls.append({'url': url, 'error': str(e), 'type': 'content_extraction'})
            return f"Error: {str(e)}", ""

    def should_skip_url(self, url):
        """Проверяем, нужно ли пропустить URL (внешние ссылки и проблемные домены)"""
        skip_domains = ['pravo.gov.ru', 'government.ru', 'kremlin.ru', 'minfin.ru']
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Пропускаем внешние домены
        if any(skip_domain in domain for skip_domain in skip_domains):
            return True
            
        # Пропускаем URL с определенными паттернами
        skip_patterns = ['post_819', 'proxy', 'nd=']
        if any(pattern in url for pattern in skip_patterns):
            return True
            
        return False

    def parse_single_category(self, start_url, category_name=""):
        """Parse a single category recursively"""
        print(f"\n{'='*80}")
        print(f"PARSING CATEGORY: {category_name}")
        print(f"Starting URL: {start_url}")
        print(f"{'='*80}")
        
        initial_visited_count = len(self.visited_urls)
        initial_data_count = len(self.data_records)
        
        queue = deque([start_url])
        self.visited_urls.add(start_url)
        
        while queue:
            current_url = queue.popleft()
            
            # Пропускаем проблемные URL
            if self.should_skip_url(current_url):
                print(f"Skipping problematic URL: {current_url}")
                continue
                
            print(f"Processing: {current_url}")
            
            # Extract content from current page
            header, content = self.extract_content(current_url)
            
            # Add to data records
            self.data_records.append({
                'id': self.current_id,
                'url': current_url,
                'header': header,
                'text': content,
                'category': category_name,
                'base_url': start_url
            })
            self.current_id += 1
            
            # Extract links from current page
            new_links = self.extract_links_from_page(current_url)
            
            # Add new links to queue
            for link in new_links:
                if link not in self.visited_urls and not self.should_skip_url(link):
                    self.visited_urls.add(link)
                    queue.append(link)
            
            print(f"  Found {len(new_links)} new links, Queue size: {len(queue)}")
            
            # Случайная задержка от 1 до 3 секунд
            time.sleep(random.uniform(1, 3))
        
        pages_processed = len(self.data_records) - initial_data_count
        print(f"✓ Category '{category_name}' completed: {pages_processed} pages processed")

    def parse_multiple_categories(self, url_list):
        """Parse multiple categories from a list of URLs"""
        categories = [
            "https://sfr.gov.ru/grazhdanam/pensionres/",
            "https://sfr.gov.ru/grazhdanam/semyam_s_detmi/",
            "https://sfr.gov.ru/grazhdanam/invalidam/",
            "https://sfr.gov.ru/grazhdanam/Informaciya_dlya_uchastnikov_SVO_i_ih_semei/",
            "https://sfr.gov.ru/grazhdanam/victims_of_industrial_accidents/",
            "https://sfr.gov.ru/grazhdanam/newregion/",
            "https://sfr.gov.ru/grazhdanam/pensionres/pens_sssr/",
            "https://sfr.gov.ru/grazhdanam/pensionres/pens_zagran/",
            "https://sfr.gov.ru/grazhdanam/workers/",
            "https://sfr.gov.ru/grazhdanam/eln/",
            "https://sfr.gov.ru/grazhdanam/social_support/",
            "https://sfr.gov.ru/grazhdanam/cosp/"
        ]
        
        # Если передан список, используем его, иначе используем стандартный
        if url_list:
            categories = url_list
        
        total_categories = len(categories)
        
        for i, category_url in enumerate(categories, 1):
            # Извлекаем название категории из URL
            category_name = category_url.split('/')[-2] if category_url.endswith('/') else category_url.split('/')[-1]
            
            print(f"\n[{i}/{total_categories}] Starting category: {category_name}")
            
            try:
                self.parse_single_category(category_url, category_name)
            except Exception as e:
                print(f"❌ Error processing category {category_name}: {e}")
                self.failed_urls.append({'url': category_url, 'error': str(e), 'type': 'category_processing'})
            
            # Задержка между категориями
            if i < total_categories:
                delay = random.uniform(2, 5)
                print(f"Waiting {delay:.1f} seconds before next category...")
                time.sleep(delay)
        
        print(f"\n{'='*80}")
        print("ALL CATEGORIES COMPLETED")
        print(f"{'='*80}")

    def save_to_dataframe(self):
        """Convert collected data to pandas DataFrame"""
        df = pd.DataFrame(self.data_records)
        return df

    def save_to_csv(self, filename="sfr_data.csv"):
        """Save data to CSV file"""
        df = self.save_to_dataframe()
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✓ Data saved to {filename}")
        
        # Сохраняем список неудачных URL
        if self.failed_urls:
            failed_df = pd.DataFrame(self.failed_urls)
            failed_filename = filename.replace('.csv', '_failed.csv')
            failed_df.to_csv(failed_filename, index=False, encoding='utf-8')
            print(f"✓ Failed URLs saved to {failed_filename}")
            
        return df

    def print_statistics(self):
        """Print parsing statistics"""
        print(f"\n{'='*80}")
        print("PARSING STATISTICS")
        print(f"{'='*80}")
        print(f"Successfully processed: {len(self.data_records)} pages")
        print(f"Failed URLs: {len(self.failed_urls)}")
        print(f"Total unique URLs visited: {len(self.visited_urls)}")
        
        # Статистика по категориям
        if self.data_records:
            df = pd.DataFrame(self.data_records)
            category_stats = df['category'].value_counts()
            print(f"\nPages per category:")
            for category, count in category_stats.items():
                print(f"  - {category}: {count} pages")
        
        if self.failed_urls:
            print(f"\nFailed URLs (first 5):")
            for failed in self.failed_urls[:5]:
                print(f"  - {failed['url']}: {failed['error']}")

def main():
    parser = SFRRecursiveParser()
    
    # Список URL для парсинга
    target_urls = [
        "https://sfr.gov.ru/grazhdanam/pensionres/",
        "https://sfr.gov.ru/grazhdanam/semyam_s_detmi/",
        "https://sfr.gov.ru/grazhdanam/invalidam/",
        "https://sfr.gov.ru/grazhdanam/Informaciya_dlya_uchastnikov_SVO_i_ih_semei/",
        "https://sfr.gov.ru/grazhdanam/victims_of_industrial_accidents/",
        "https://sfr.gov.ru/grazhdanam/newregion/",
        "https://sfr.gov.ru/grazhdanam/pensionres/pens_sssr/",
        "https://sfr.gov.ru/grazhdanam/pensionres/pens_zagran/",
        "https://sfr.gov.ru/grazhdanam/workers/",
        "https://sfr.gov.ru/grazhdanam/eln/",
        "https://sfr.gov.ru/grazhdanam/social_support/",
        "https://sfr.gov.ru/grazhdanam/cosp/"
    ]
    
    print("SFR.GOV.RU MULTI-CATEGORY RECURSIVE PARSER")
    print("="*80)
    print(f"Processing {len(target_urls)} categories")
    print("="*80)
    
    try:
        # Start parsing all categories
        parser.parse_multiple_categories(target_urls)
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"sfr_all_categories_{timestamp}.csv"
        df = parser.save_to_csv(filename)
        
        # Print statistics
        parser.print_statistics()
        
        # Display summary
        print(f"\nFirst 5 records:")
        print(df[['id', 'category', 'url', 'header']].head().to_string(index=False))
        
    except KeyboardInterrupt:
        print("\n\nParsing interrupted by user. Saving current progress...")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        df = parser.save_to_csv(f"sfr_partial_{timestamp}.csv")
        parser.print_statistics()
        
    except Exception as e:
        print(f"\n\nCritical error: {e}")
        print("Saving current progress...")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        df = parser.save_to_csv(f"sfr_error_{timestamp}.csv")
        parser.print_statistics()

if __name__ == '__main__':
    main()