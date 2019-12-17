import scrapy
import json
import pickle

class XBizSpider(scrapy.Spider):
	name = "nd_biz"

	def start_requests(self):
		payload = """{"SEARCH_VALUE":"x","STARTS_WITH_YN":'true',"ACTIVE_ONLY_YN":'true'}"""
		yield scrapy.Request(url="https://firststop.sos.nd.gov/api/Records/businesssearch",
							 method='POST',
							 headers={'content-type': 'application/json'},
							 body=payload,
							 )

	def parse(self, response):
        """For parsing the main list of business which is returned by the search request"""

        # parsing SOURCE_ID's from main list of business entities
		dirty_ids = response.selector.re('"ID":\d+')
		clean_ids = [x.split(':')[1] for x in dirty_ids]
		res_json = json.loads(response.text) #main list of business to json
		biz_title = {}

		for id in clean_ids:
			# Store ID & Title
			biz_title[id] = res_json["rows"][id]['TITLE'][0] 

			# Request Details
			yield scrapy.Request(url=f"https://firststop.sos.nd.gov/api/FilingDetail/business/{id}/false",
		                         callback=self.parse_biz,
				                 )
		# Data referred to in .ipynb
		pickle.dump(biz_title, open('biz_title.p','wb'))


	def parse_biz(self, response):
		"""For parsing indivdual buissness' FilingDetail"""

		# xpath expressions 
		maddy_xp=\
		"//DRAWER/DRAWER_DETAIL_LIST/DRAWER_DETAIL/LABEL[contains(text(), 'Mailing Address')]//following-sibling::VALUE/text()"
		owner_xp =\
		"//DRAWER/DRAWER_DETAIL_LIST/DRAWER_DETAIL/LABEL[contains(text(), 'Owner Name')]//following-sibling::VALUE/text()"
		agent_xp =\
		"//DRAWER/DRAWER_DETAIL_LIST/DRAWER_DETAIL/LABEL[contains(text(), 'Registered Agent')]//following-sibling::VALUE/text()"

		id = response.request.url.split('/')[-2]
		maddress = response.xpath(maddy_xp).get()
		owner = response.xpath(owner_xp).get()
		agent = response.xpath(agent_xp).get()

		# Written to JSON Lines when this is invoked on the command line
		yield{'id':id,'maddress': maddress,'owner': owner,'agent': agent,}