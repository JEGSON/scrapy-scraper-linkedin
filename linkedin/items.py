# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkedInCompanyProfileItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    summary = scrapy.Field()
    industry = scrapy.Field()
    size = scrapy.Field()
    founded = scrapy.Field()


class LinkedInJobItem(scrapy.Item):
    job_title = scrapy.Field()
    job_detail_url = scrapy.Field()
    job_listed = scrapy.Field()
    company_name = scrapy.Field()
    company_link = scrapy.Field()
    company_location = scrapy.Field()



class LinkedInPeopleProfileItem(scrapy.Item):
    profile = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    location = scrapy.Field()
    followers = scrapy.Field()
    connections = scrapy.Field()
    about = scrapy.Field()
    experience = scrapy.Field()
    education = scrapy.Field()
