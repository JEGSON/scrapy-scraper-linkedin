import json
import scrapy
from linkedin.items import LinkedInCompanyProfileItem


class LinkedInCompanyProfileSpider(scrapy.Spider):
    name = "linkedin_company_profile"
    api_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=python&location=United%2BStates&geoId=103644278&trk=public_jobs_jobs-search-bar_search-submit&start=' 

    # List of LinkedIn company pages to scrape
    company_pages = [
        'https://www.linkedin.com/company/usebraintrust?trk=public_jobs_jserp-result_job-search-card-subtitle',
        'https://www.linkedin.com/company/centraprise?trk=public_jobs_jserp-result_job-search-card-subtitle'
    ]

    def start_requests(self):
        """
        Method to start the scraping process by sending requests to company pages.
        """
        for index, company_url in enumerate(self.company_pages):
            yield scrapy.Request(url=company_url, callback=self.parse_response, meta={'company_index_tracker': index})

    def parse_response(self, response):
        """
        Method to parse the response from a company page.
        """
        company_index_tracker = response.meta['company_index_tracker']
        self.log(f'Scraping page {company_index_tracker+1} of {len(self.company_pages)}')

        # Initialize a LinkedInCompanyProfileItem
        company_item = LinkedInCompanyProfileItem(
            name=response.css('.top-card-layout__entity-info h1::text').get(default='not-found').strip(),
            summary=response.css('.top-card-layout__entity-info h4 span::text').get(default='not-found').strip()
        )

        try:
            # Extract various details about the company
            company_details = response.css('.core-section-container__content .mb-2')

            # Extract industry information
            company_industry_line = company_details[1].css('.text-md::text').getall()
            company_item['industry'] = company_industry_line[1].strip()

            # Extract company size information
            company_size_line = company_details[2].css('.text-md::text').getall()
            company_item['size'] = company_size_line[1].strip()

            # Extract company founded information
            company_size_line = company_details[5].css('.text-md::text').getall()
            company_item['founded'] = company_size_line[1].strip()

        except IndexError:
            self.log("Error: Skipped Company - Some details missing")

        # Yield the LinkedInCompanyProfileItem
        yield company_item

        company_index_tracker += 1
        if company_index_tracker < len(self.company_pages):
            next_url = self.company_pages[company_index_tracker]
            # Send a request for the next company page
            yield scrapy.Request(url=next_url, callback=self.parse_response, meta={'company_index_tracker': company_index_tracker})

    def read_urls_from_jobs_file(self):
        """
        Method to read company URLs from a jobs file.
        """
        self.company_pages = []
        with open('jobs.json') as file:
            jobs_from_file = json.load(file)

            for job in jobs_from_file:
                if job['company_link'] != 'not-found':
                    self.company_pages.append(job['company_link'])

        # Remove any duplicate links to prevent spider shutdown on duplicates
        self.company_pages = list(set(self.company_pages))
