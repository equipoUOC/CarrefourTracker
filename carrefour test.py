import scrapy
from scrapy.crawler import CrawlerProcess

class CarrefourItem(scrapy.Item):
    producto = scrapy.Field()
    precio = scrapy.Field()
    

class CarrefourSpider(scrapy.Spider):

    name = "carrefourSpider"
    def start_requests(self):
        url=['https://www.carrefour.es/supermercado/el-mercado/pescaderia/pescado-fresco/N-ij568u/c']
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        item = CarrefourItem()
        item['producto'] = response.css('p.title-product__nombre-producto ::text').extract().strip()
        item['precio'] = response.css('span.price__precio-producto ::text').extract().strip()
            
        yield item

#scrapy crawl carrefourSpider -o Carrefour.csv