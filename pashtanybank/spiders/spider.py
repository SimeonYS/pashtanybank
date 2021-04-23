import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import PpashtanybankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class PpashtanybankSpider(scrapy.Spider):
	name = 'pashtanybank'
	start_urls = ['https://pashtanybank.com.af/all-news']

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@title="Go to next page"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="font-weight-light"]/text()').get()
		date = re.findall(r'\w+\s\d+\s\d+', date)
		title = response.xpath('//span[@class="field field--name-title field--type-string field--label-hidden"]/text()').get()
		content = response.xpath('//article[@class="article"]//text()[not (ancestor::h1 or ancestor::div[@class="clearfix"] or ancestor::figure)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=PpashtanybankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
