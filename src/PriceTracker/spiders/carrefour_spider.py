import datetime
import pandas as pd
import pathlib
import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import PricetrackerItem

class CarrefourSpider(scrapy.Spider):
    name = "carrefourSpider"
    fecha = '{0:%d%m%Y_%H%M}'.format(datetime.datetime.now())
    fileName = 'CarrefourDailyPricing_' + fecha + '.csv'
    filePath = '../CSVdata/' + fileName
    # custom_settings = {'FEED_URI': filePath, 'FEED_FORMAT': 'csv'}
    custom_settings = {'FEEDS': {pathlib.Path(filePath): {'format': 'csv',
                                                'encoding': 'utf8',
                                                'store_empty': True,
                                                'fields': ['seccion',
                                                           'categoria',
                                                           'descripcion',
                                                           'precio_Kg_L_ud',
                                                           'precio',
                                                           'precioPrevio',
                                                           'precioOferta',
                                                           'promocion',
                                                           'enlace'],}}}

    def start_requests(self):
        urls=['https://www.carrefour.es/supermercado/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_seccion)

    def descargar_links(self, response):
        # Se captura el título de la web actual y se utiliza como nombre del
        # fichero html que se guarda
        titulo = response.css('title::text').extract_first()
        html_file = './web/' + str(titulo) + '.html'
        with open( html_file, 'wb' ) as fout:
            fout.write( response.body )

    def parse_seccion(self, response):
        # Extraemos el código html correspodiente a cada sección
        listaSecciones = response.css('li.level2-item')
        # print("Se han encontrado {} secciones.".format(len(listaSecciones)))
        # Para cada sección, seguimos el enlace hacia las diferentes categorías
        for seccion in listaSecciones[0:2]:
            # Se captura el nombre de la sección
            nombreSeccion = seccion.css('a ::text').extract_first()
            # print("Seccion: {}".format(nombreSeccion))
            # Se extra el link de esta sección
            link = seccion.css('a::attr(href)').extract_first()
            # print("linkSeccion: {}".format(link))
            next_page_url = response.urljoin(link)
            # print("Seccion siguiente: {}".format(next_page_url))
            yield response.follow(url=next_page_url,
                                  callback=self.parse_categoria,
                                  cb_kwargs={'seccion':nombreSeccion})

    def parse_categoria(self, response, seccion):
        # Extraemos el código html de las diferentes categorias
        listaCategorias = response.css('div.category')
        # print("Se han encontrado {} categorias.".format(len(listaCategorias)))
        for categoria in listaCategorias[0:2]:
            nombreCategoria = categoria.css('p.nombre-categoria::text')\
                .extract_first()
            # print("Categoría: {}".format(nombreCategoria))
            # Se extrae el link de esta categoria
            link = categoria.css('a::attr(href)').extract_first()
            # print("linkCategoria: {}".format(link))
            next_page_url = response.urljoin(link)
            # print("Categoria siguiente: {}".format(next_page_url))
            yield response.follow(url=next_page_url,
                                  callback=self.parse_productos,
                                  cb_kwargs={'seccion':seccion,
                                             'categoria': nombreCategoria})

    def parse_productos(self, response, seccion, categoria):
        # Se filtran los "product-card-item" para no mezclar precios
        items_producto = response.css('article.product-card-item')
        # print("Se han encontrado {} productos".format(len(items_producto)-1))
        # Se recorre cada item para extraer el nombre, los precios y las
        # ofertas
        for producto in items_producto[0:2]:
            descripcion = producto.css('p.title-product ::text')\
                .extract_first()
            # Si hay descripción asignamos los valores, sino se comprueba si
            # hay página siguiente
            if(descripcion):
                item = PricetrackerItem()
                item['seccion']=seccion
                item['categoria']=categoria
                # Buscamos los nombres del producto
                item['descripcion'] = descripcion
                item['precio'] = producto.css('span.price ::text')\
                    .extract_first()
                item['precioPrevio'] = producto.css('strike ::text')\
                    .extract_first()
                item['precioOferta'] = producto.css('span.price-less ::text')\
                    .extract_first()
                # Se captura el primer match del regex
                item['precio_Kg_L_ud'] = producto.css('p.format-price::text')\
                    .re('.*\|\s(.*)')[0]
                item['promocion'] = producto.css('p.promocion-copy ::text')\
                    .extract_first()
                link = producto.css('a.js-gap-product-click-super ::attr(href)')\
                    .extract_first()
                item['enlace'] = response.urljoin(link)
                yield item
            else:
                # Extraemos información de las páginas siguientes de la
                # misma categoria
                next_page_url = response.css('a.next::attr(href)')\
                    .extract_first()
                if next_page_url:
                    next_page_url = response.urljoin(next_page_url)
                    # print("Pagina siguiente: {}".format(next_page_url))
                    yield response.follow(url=next_page_url,
                                          callback=self.parse_productos)
