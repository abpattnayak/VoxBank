# coding=utf-8
from __future__ import absolute_import
import scrapy, datetime, re
from scrapy import log
from dateutil.parser import parse
from voxilloBanking.items import VoxillobankingItem
from scrapy.http import Request
from selenium import webdriver

class VoxRabobankSpider(scrapy.Spider):
	name = "vox_ing_spider"

	def start_requests(self):
		urls = ["https://www.ing.nl/particulier/hypotheken/actuele-hypotheekrente/index.html"]
		for url in urls:
			yield scrapy.Request(url = url, callback = self.parseRabobank)

	def parseRabobank(self, response):

		item = VoxillobankingItem()
		item['CountryCode'] = 'NL'
		item['ProviderName'] = 'ING'
		item['CheckDate'] = str(datetime.datetime.now().strftime("%Y-%m-%d"))
		
		product1 = "Annuïteitenhypotheek"
		product2 = "Lineaire hypotheek"

		self.driver = webdriver.Chrome()
		#self.driver.set_window_size(1120,550)
		self.driver.get(response.url)
		sel = scrapy.Selector(text = self.driver.page_source)
		log.msg("URL: --------- %s" %response.url, level = log.DEBUG)

		#validity since date search
		validString = sel.xpath("//p[contains(@class, 'small-font') and contains(text(),'Deze tarieven gelden voor nieuwe offertes en renteaanpassingen voor bestaande hypotheken uitgebracht vanaf')]/text()").extract()[0]
		validString = self.changeMonth((str(validString)))
		
		regex = r"([0-9]+\s+[a-z]+\s+[0-9])\w+"
		pattern = re.compile(regex)
		matches = re.search(regex, validString, re.DOTALL)
		if matches:
			date = parse(matches.group(0))
			date = str(date).split()[0]
		#og.msg("Valid Since Date -------- %s" %date, level = log.DEBUG)
		item["ValidSince"] = date
		
		

		tables =  sel.xpath('//table[@class="table table-b table-lr-unpadded l-mb-0"]/tbody')
		for i in range(0,2): #tables
			rows = tables[i].xpath("tr")
			headers = tables[i].xpath("tr/td/strong/text()").extract()
			for j in range(1,len(rows)):
				rowData = rows[j].xpath("td/text()").extract()
				for k in range(1, len(rowData)):
					item['ProductName'] = "ING" + product1
					item['LoanType'] = product1
					item['Period'] = str(rowData[0]).replace("jaar","").strip()
					data = str(rowData[k]).replace(",",".").replace("%","").strip()
					item['Rate'] = str(float(data)+0.25)
					if(headers[k-1]==">101%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "101"
						item['CoverageEnd'] = ""
						yield item
						continue
					nonBreakSpace = u'\xa0'
					headers[k-1] = str(headers[k-1].replace(nonBreakSpace,"").encode("utf-8").strip()).replace("≤","").replace(">","")
					log.msg("Headers -------- %s" %headers[k-1], level = log.DEBUG)
					if(headers[k-1]=="NHG"):
						item['NHG'] = "Y"
						item['CoverageStart'] = ""
						item['CoverageEnd'] = ""
					elif(headers[k-1]=="55%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "0"
						item['CoverageEnd'] = "55"
					elif(headers[k-1]=="60%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "56"
						item['CoverageEnd'] = "60"
					elif(headers[k-1]=="65%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "61"
						item['CoverageEnd'] = "65"
					elif(headers[k-1]=="70%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "66"
						item['CoverageEnd'] = "70"
					elif(headers[k-1]=="75%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "71"
						item['CoverageEnd'] = "75"
					elif(headers[k-1]=="80%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "76"
						item['CoverageEnd'] = "80"
					elif(headers[k-1]=="85%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "81"
						item['CoverageEnd'] = "85"
					elif(headers[k-1]=="90%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "86"
						item['CoverageEnd'] = "90"
					elif(headers[k-1]=="95%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "91"
						item['CoverageEnd'] = "95"
					elif(headers[k-1]=="101%"):
						item['NHG'] = "N"
						item['CoverageStart'] = "96"
						item['CoverageEnd'] = "101"
					yield item	

		#log.msg("DIVS: --------- %s" %(divRows), level = log.DEBUG)
		self.driver.close()

	def changeMonth(self,date):
		date = date.replace("januari","january").replace("februari","february").replace("maart","march").replace("mei","may").replace("juni","june").replace("juli","july").replace("augustus","august").replace("oktober","october")
		return date