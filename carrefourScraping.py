import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
import schedule
import time
import datetime
import sys

class CarrefourSpider(scrapy.Spider):
    name = "carrefourSpider"

    def start_requests(self):
        urls=['https://www.carrefour.es/supermercado/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_seccion,
                                 headers=headers)

    def descargar_links(self, response):
        # Se captura el título de la web actual y se utiliza como nombre del
        # fichero html que se guarda
        titulo = response.css('title::text').extract_first()
        html_file = './web/' + str(titulo) + '.html'
        with open( html_file, 'wb' ) as fout:
            fout.write( response.body )

    def parse_seccion(self, response):
        #Extraemos links de diferentes secciones
        listaSecciones = response.css('div#inner-level-list a::attr(href)')\
            .extract()
        for link in listaSecciones:
            next_page_url = response.urljoin(link)
            # print("Seccion siguiente: {}".format(next_page_url))
            yield response.follow(url=next_page_url,
                                  callback=self.parse_categoria,
                                  headers=headers)

    def parse_categoria(self, response):
        #Extraemos links de las diferentes categorias
        listaCategorias = response.css('div.category-box a::attr(href)')\
            .extract()
        for link in listaCategorias:
            next_page_url = response.urljoin(link)
            # print("Categoria siguiente: {}".format(next_page_url))
            yield response.follow(url=next_page_url,
                                  callback=self.parse_productos,
                                  headers=headers)

    def parse_productos(self, response):
        # Se filtran los "product-card-item" para no mezclar precios
        items_producto = response.css('article.product-card-item')
        # print("Se han encontrado {} productos".format(len(items_producto)-1))
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

        #Extraemos información de las páginas siguientes de esta categoria
        next_page_url = response.css('a.next::attr(href)').extract_first()
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            # print("Pagina siguiente: {}".format(next_page_url))
            yield response.follow(url=next_page_url,
                                  callback=self.parse_productos,
                                  headers=headers)

if __name__ == '__main__':
    
    # Se crea una lista donde se guardarán todos los productos encontrados
    lista_productos=[]

    # Se configura la cabecera que se usará para hacer las peticiones y evitar
    # ser bloqueados
    headers={"User-Agent": "Mozilla/5.0 (Windows\
NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.1\
11 Safari/537.36"}
    # Se inicializa y se crea la araña que recorre la web
    process = CrawlerProcess()
    process.crawl(CarrefourSpider)
    process.start()

    fecha = '{0:%Y%m%d_%H%M}'.format(datetime.datetime.now())
    fileName = 'ProductosCarrefour_' + fecha + '.csv'
    filePath = './CSVdata/' + fileName
    # Si hay productos en la lista se crea un fichero con los datos
    if lista_productos:
        # Se crea un dataframe con todos los valores y se guarda como CSV
        productos = pd.DataFrame(lista_productos)
        productos.to_csv(filePath, columns=['Productos', 'Precio/Kg',
                                            'Precios', 'PrecioPrevio',
                                            'Ofertas', 'Promociones'],
                         encoding='utf-8-sig')

# Programamos la araña para que recorra la web una vez todos los días a las
# 8hrs
schedule.every().day.at("08:00").do(CarrefourSpider())

while True:
    schedule.run_pending()
    time.sleep(1)
