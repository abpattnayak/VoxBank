# coding=utf-8
from __future__ import absolute_import
import scrapy, datetime, re
from scrapy import log
from dateutil.parser import parse
from voxilloBanking.items import VoxillobankingItem
from scrapy.http import Request
from selenium import webdriver

class VoxRabobankSpider(scrapy.Spider):
	name = "vox_rabobank_spider"

	def start_requests(self):
		urls = ["https://www.rabobank.nl/particulieren/hypotheek/hypotheekrente/?intcamp=pa-hypotheek&inttype=tegel-hypotheekrente&intsource=hypotheek"]
		for url in urls:
			yield scrapy.Request(url = url, callback = self.parseRabobank)

	def parseRabobank(self, response):

		item = VoxillobankingItem()
		item['CountryCode'] = 'NL'
		item['ProviderName'] = 'Rabobank'
		item['CheckDate'] = str(datetime.datetime.now().strftime("%Y-%m-%d"))
		item['LoanType'] = "Annuiteitenhypotheek"
		item['NHG'] = "N"
		product1 = "Basisvoorwaarden"
		product2 = "Plusvoorwaarden"

		self.driver = webdriver.Chrome()
		#self.driver.set_window_size(1120,550)
		self.driver.get(response.url)
		sel = scrapy.Selector(text = self.driver.page_source)
		log.msg("URL: --------- %s" %response.url, level = log.DEBUG)

		#validity since date search
		validString = sel.xpath("//li[contains(text(),'totdat wij de tarieven wijzigen')]/text()").extract()[0]
		validString = self.changeMonth((str(validString)))

		regex = r"([0-9]+\s+[a-z]+\s+[0-9])\w+"
		pattern = re.compile(regex)
		matches = re.search(regex, validString, re.DOTALL)
		if matches:
			date = parse(matches.group(0))
			date = str(date).split()[0]

		item["ValidSince"] = date
		
		divRows = sel.xpath("//div[contains(@class,'s14-lamella--shadow')]")
		for div in divRows:
			head = div.xpath('.//h2//text()').extract()[0]
			#log.msg("Head -------- %s" %head, level = log.DEBUG)
			if(str(head) == "Alle rentepercentages hypotheek met Basisvoorwaarden"):
				item['ProductName'] = "Rabobank" + product1
				tableRows = div.xpath(".//table/tbody/tr")
				headers = tableRows[0].xpath("td/strong/text()").extract()
				for i in range(1,len(tableRows)):
					rowData = tableRows[i].xpath('td/text()').extract()
					item['Period'] = str(rowData[0]).replace("jaar","")
					#log.msg("Period: ------- %s" %item['Period'], level = log.DEBUG)
					for j in range(1,len(rowData)):
						item['Rate'] = str(rowData[j]).replace(",",".").replace("%","").strip()
						h = headers[j-1]
						log.msg("headers: ----- %s" %h, level = log.DEBUG)
					
						if(h=="Met NHG of tot en met 67,5% van de marktwaarde*"):
							item['CoverageStart'] = "0"
							item['CoverageEnd'] = "67.5"
						elif(h=="Meer dan 67,5% tot en met 90% van de marktwaarde*"):
							item['CoverageStart'] = "68.5"
							item['CoverageEnd'] = "90"
						elif(h=="Meer dan 90% van de marktwaarde*"):
							item['CoverageStart'] = "91"
							item['CoverageEnd'] = ""
						yield item

			elif(str(head) == "Alle rentepercentages hypotheek met Plusvoorwaarden"):
				item['ProductName'] = "Rabobank" + product2
				tableRows = div.xpath(".//table/tbody/tr")
				headers = tableRows[0].xpath("td/strong/text()").extract()
				#log.msg("tableRows: ----- %s" %tableRows, level = log.DEBUG)
				for i in range(1,len(tableRows)):
					rowData = tableRows[i].xpath('td/text()').extract()
					item['Period'] = str(rowData[0]).replace("jaar","")
					#log.msg("Period: ------- %s" %item['Period'], level = log.DEBUG)
					for j in range(1,len(rowData)):
						item['Rate'] = str(rowData[j]).replace(",",".").replace("%","").strip()
						h = headers[j-1]
						if(h=="Met NHG of tot en met 67,5% van de marktwaarde*"):
							item['CoverageStart'] = "0"
							item['CoverageEnd'] = "67.5"
						elif(h=="Meer dan 67,5% tot en met 90% van de marktwaarde*"):
							item['CoverageStart'] = "68.5"
							item['CoverageEnd'] = "90"
						elif(h=="Meer dan 90% van de marktwaarde*"):
							item['CoverageStart'] = "91"
							item['CoverageEnd'] = ""
						yield item
			
		#log.msg("DIVS: --------- %s" %(divRows), level = log.DEBUG)
		self.driver.close()

	def changeMonth(self,date):
		date = date.replace("januari","january").replace("februari","february").replace("maart","march").replace("mei","may").replace("juni","june").replace("juli","july").replace("augustus","august").replace("oktober","october")
		return date