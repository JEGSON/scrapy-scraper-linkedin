import scrapy
from linkedin.items import LinkedInPeopleProfileItem  # Update with your actual project name

class LinkedInPeopleProfileSpider(scrapy.Spider):
    name = "linkedin_people_profile"

    custom_settings = {
        'FEEDS': {'data/%(name)s_%(time)s.jsonl': {'format': 'jsonlines',}}
    }

    def start_requests(self):
        """
        Method to start the scraping process by sending requests to LinkedIn profiles.
        """
        profile_list = ['reidhoffman']
        for profile in profile_list:
            linkedin_people_url = f'https://www.linkedin.com/in/{profile}/'
            yield scrapy.Request(url=linkedin_people_url, callback=self.parse_profile,
                                 meta={'profile': profile, 'linkedin_url': linkedin_people_url})

    def parse_profile(self, response):
        """
        Method to parse LinkedIn profile details.
        """
        item = LinkedInPeopleProfileItem({
            'profile': response.meta['profile'],
            'url': response.meta['linkedin_url'],
            'name': response.css("section.top-card-layout h1::text").get('').strip(),
            'description': response.css("section.top-card-layout h2::text").get('').strip()
        })

        # Parse Location
        try:
            item['location'] = response.css('div.top-card__subline-item::text').get()
        except:
            item['location'] = response.css('span.top-card__subline-item::text').get('').strip()
            if 'followers' in item['location'] or 'connections' in item['location']:
                item['location'] = ''

        item.update({
            'followers': '',
            'connections': ''
        })

        for span_text in response.css('span.top-card__subline-item::text').getall():
            if 'followers' in span_text:
                item['followers'] = span_text.replace(' followers', '').strip()
            if 'connections' in span_text:
                item['connections'] = span_text.replace(' connections', '').strip()

        # Parse ABOUT SECTION
        item['about'] = response.css('section.summary div.core-section-container__content p::text').get()

        # Parse EXPERIENCE SECTION
        item['experience'] = []
        for block in response.css('li.experience-item'):
            experience = {
                'organisation_profile': block.css('h4 a::attr(href)').get('').split('?')[0],
                'location': block.css('p.experience-item__location::text').get('').strip()
            }

            try:
                experience['description'] = block.css('p.show-more-less-text__text--more::text').get('').strip()
            except:
                experience['description'] = block.css('p.show-more-less-text__text--less::text').get('').strip()

            date_ranges = block.css('span.date-range time::text').getall()
            if len(date_ranges) == 2:
                experience.update({
                    'start_time': date_ranges[0],
                    'end_time': date_ranges[1],
                    'duration': block.css('span.date-range__duration::text').get('')
                })
            elif len(date_ranges) == 1:
                experience.update({
                    'start_time': date_ranges[0],
                    'end_time': 'present',
                    'duration': block.css('span.date-range__duration::text').get('')
                })
            else:
                experience.update({
                    'start_time': '',
                    'end_time': '',
                    'duration': ''
                })

            item['experience'].append(experience)

        # Parse EDUCATION SECTION
        item['education'] = []
        for block in response.css('li.education__list-item'):
            education = {
                'organisation': block.css('h3::text').get('').strip(),
                'organisation_profile': block.css('a::attr(href)').get('').split('?')[0],
                'course_details': ' '.join(block.css('h4 span::text').getall()).strip(),
                'description': block.css('div.education__item--details p::text').get('').strip()
            }

            date_ranges = block.css('span.date-range time::text').getall()
            if len(date_ranges) == 2:
                education.update({
                    'start_time': date_ranges[0],
                    'end_time': date_ranges[1]
                })
            elif len(date_ranges) == 1:
                education.update({
                    'start_time': date_ranges[0],
                    'end_time': 'present'
                })
            else:
                education.update({
                    'start_time': '',
                    'end_time': ''
                })

            item['education'].append(education)

        yield item
