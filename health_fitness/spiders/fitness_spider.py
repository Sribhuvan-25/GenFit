import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.http import HtmlResponse

class FitnessSpider(scrapy.Spider):
    name = 'fitness_spider'

    # List of URLs to scrape
    start_urls = [
        'https://www.healthline.com/nutrition/healthy-eating-tips',  # Static
        'https://www.verywellfit.com/how-to-start-a-fitness-routine-1230922',  # Dynamic (Selenium)
        'https://www.bodybuilding.com/content/7-day-home-workout-challenge.html',  # Static
        'https://www.mayoclinic.org/healthy-lifestyle/fitness/expert-answers/fitness/faq-20058000',  # Static
    ]

    def __init__(self, *args, **kwargs):
        super(FitnessSpider, self).__init__(*args, **kwargs)

        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Optional: run in headless mode (no UI)
        chrome_options.add_argument("--no-sandbox")  # Disable sandbox for Linux environments
        chrome_options.add_argument("--disable-dev-shm-usage")  # For environments like Docker

        # Initialize the WebDriver with the ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    def parse(self, response):
        """Process each page and extract data."""
        if "verywellfit" in response.url:
            # For dynamic content pages, use Selenium to render the page
            self.driver.get(response.url)
            self.driver.implicitly_wait(3)  # Wait for JS to load
            page_source = self.driver.page_source
            response = HtmlResponse(url=self.driver.current_url, body=page_source, encoding='utf-8')

        # Extract common data (Title, Description, URL)
        title = response.xpath('//h1/text()').get()
        description = response.xpath('//div[@class="article-body"]//p/text()').getall()

        # Yield the extracted data
        yield {
            'title': title.strip() if title else 'N/A',
            'description': ' '.join([p.strip() for p in description]) if description else 'N/A',
            'url': response.url
        }

    def close(self, reason):
        """Close the Selenium WebDriver after scraping."""
        self.driver.quit()
