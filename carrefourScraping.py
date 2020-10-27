import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess

class CarrefourSpider(scrapy.Spider):
    name = "carrefourSpider"

    def start_requests(self):
        urls=['https://www.carrefour.es/supermercado/el-mercado/pescaderia/pescado-fresco/N-ij568u/c']
        for url in urls:
            # Se configura la petición con un userAgent para evitar ser
            # bloqueado
            yield scrapy.Request(url=url, callback=self.parse_productos,
                                 headers={"User-Agent": "Mozilla/5.0 (Windows\
NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.1\
11 Safari/537.36"})

    def parse_productos(self, response):
        filePath = 'ProductosCarrefour.csv'
        # Se filtran los "product-card-item" para no mezclar precios
        items_producto = response.css('article.product-card-item')
        print("Se han encontrado {} productos".format(len(items_producto)-1))
        lista_productos=[]
        # Se recorre cada item para extraer el nonmbre, los precios y las
        # ofertas
        for item in items_producto:
            #Buscamos los nombres del producto
            producto = item.css('p.title-product ::text').extract_first()
            precio = item.css('span.price ::text').extract_first()
            precioAnt = item.css('strike ::text').extract_first()
            precioOferta = item.css('span.price-less ::text').extract_first()
            precioKg = item.css('p.format-price ::text').extract_first()
            promocion = item.css('p.promocion-copy ::text').extract_first()
            # Se añade a la lista un diccionario con los valores capturados
            lista_productos.append({'Productos':producto,
                                    'Precio/Kg':precioKg,
                                    'Precios':precio,
                                    'PrecioPrevio':precioAnt,
                                    'Ofertas':precioOferta,
                                    'Promociones':promocion})

        # Se crea un dataframe con todos los valores y se guarda como CSV
        productos = pd.DataFrame(lista_productos)
        productos.to_csv(filePath, columns=['Productos', 'Precio/Kg',
                                            'Precios', 'PrecioPrevio',
                                            'Ofertas', 'Promociones'],
                         encoding='utf-8-sig')

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(CarrefourSpider)
    process.start()