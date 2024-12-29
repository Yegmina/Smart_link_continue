# company_spider.py
import sqlite3
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import os

def get_db_path():
    """Get the absolute path to the database file."""
    spider_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up 3 levels: spiders -> company_scraper -> company_scraper -> scraping_and_db
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(spider_dir)))
    return os.path.join(root_dir, 'scraped_data.db')

def get_unscraped_domains(db_path):
    """
    Return a list of all domains from *both* PRH and XXX tables
    that do NOT exist in 'scraped_pages'.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # This query picks any domain from the two "company" tables
    # that is NOT in `scraped_pages`
    # The LIMIT is how many pages that haven't been scraped we go through during this run.
    query = """
    SELECT domain FROM (
        SELECT domain FROM scraped_companies_PRH
    )
    WHERE domain NOT IN (
        SELECT DISTINCT domain FROM scraped_pages
    )
    
    LIMIT 50
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    # rows will be a list of tuples, e.g. [('example.com',), ('another.org',)]
    return [row[0] for row in rows]

class CompanySpider(CrawlSpider):
    name = 'company_spider'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_path = get_db_path()

        # 1) Get unscraped domains from possibly many tables
        unscraped = get_unscraped_domains(self.db_path)

        self.start_urls = []
        self.allowed_domains = []

        for domain in unscraped:
            # Reconstruct a URL by prefixing http:// if needed
            # (Or fetch the actual URL from each table alternatively)
            url = f"http://{domain}"
            self.start_urls.append(url)
            self.allowed_domains.append(domain)

        self.rules = (
            Rule(
                LinkExtractor(allow_domains=self.allowed_domains, unique=True),
                callback='parse_item',
                follow=True
            ),
        )
        self._compile_rules()

    def parse_item(self, response):
        domain = response.url.split("//")[-1].split("/")[0].replace('www.', '')
        text_content = ' '.join(response.xpath('//body//text()').getall()).strip()

        conn = sqlite3.connect(self.db_path)
        with conn:
            conn.execute('''
                INSERT INTO scraped_pages (domain, page_url, content)
                VALUES (?, ?, ?)
            ''', (domain, response.url, text_content))
        conn.close()
