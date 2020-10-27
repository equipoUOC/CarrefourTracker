import scrapy
from scrapy.crawler import CrawlerProcess

class CarrefourSpider(scrapy.Spider):
    name = "carrefourspider"
    def start_requests(self):
        url=['https://www.carrefour.es/supermercado/el-mercado/pescaderia/pescado-fresco/N-ij568u/c']
        yield scrapy.Request(url=url, callback=self.parse)

    def parse_productos(self, response):
        #Buscamos los nombres de los productos
        nombres_productos = response.css('p.title-product__nombre-producto ::text').extract().strip()
        return nombres_productos
    
    def parse_precios(self, response):
        #Buscamos los precios de los productos
        precios_productos = response.css('span.price__precio-producto ::text').extract().strip
        return precios_productos
        #Creamos archivo csv
        filepath = 'carrefourSheet.csv'
        with open(filepath, 'w') as f:
            f.writelines([precio + 'n/' for precio in precios_productos])
    
    #process = CrawlerProcess()
    #process.crawl(carrefourspider)
    #process.start()