import datetime
import pathlib
import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import PricetrackerItem

class CarrefourSpider(scrapy.Spider):
    name = "carrefourSpider"
    fecha = '{0:%d%m%Y_%H%M}'.format(datetime.datetime.now())
    fileName = 'CarrefourDailyPricing_' + fecha + '.csv'
    filePath = '../CSVdata/' + fileName
    custom_settings = {'FEEDS': {pathlib.Path(filePath): {'format': 'csv',
                                                'encoding': 'utf8',
                                                'fields': ['seccion',
                                                           'categoria',
                                                           'descripcion',
                                                           'precioMedida',
                                                           'precio',
                                                           'precioPrevio',
                                                           'precioOferta',
                                                           'promocion',
                                                           'enlace'],}}}

    def start_requests(self):
        urls=['https://www.carrefour.es/supermercado/']
        for url in urls:
            try:
                yield scrapy.Request(url=url, callback=self.parse_seccion)
            except Exception as e:
                raise ValueError("ERROR haciendo petición a la url {}\n{}"
                                 .format(url, e))

    def descargar_links(self, response):
        try:
            # Se captura el título de la web actual y se utiliza como nombre del
            # fichero html que se guarda
            titulo = response.css('title::text').extract_first()
            html_file = './web/' + str(titulo) + '.html'
            with open( html_file, 'wb' ) as fout:
                fout.write( response.body )
        except Exception as e:
            raise ValueError("ERROR guardando el html:\n{}".format(e))

    def parse_seccion(self, response):
        # Se extraen y se siguen todos los enlaces encontrados correspondientes
        # a las diferentes secciones
        yield from response.follow_all(css='li.level2-item a',
                                       callback=self.parse_categoria)

    def parse_categoria(self, response):
        # Se extraen y se siguen todos los enlaces encontrados correspondientes
        # a las diferentes categorias
        yield from response.follow_all(css='div.category a',
                                       callback=self.parse_productos)

    def parse_productos(self, response):
        # Se filtran los "product-card-item" para no mezclar precios
        items_producto = response.css('article.product-card-item')
        # print("Se han encontrado {} productos".format(len(items_producto)-1))
        # Se recorre cada item para extraer el nombre, los precios y las
        # ofertas
        for producto in items_producto:
            try:
                descripcion = producto.css('p.title-product ::text')\
                    .extract_first()
                # Si hay descripción asignamos los valores, sino se comprueba si
                # hay página siguiente
                if(descripcion):
                    item = PricetrackerItem()
                    item['seccion'] = response.css('li.subCategoryName').xpath(
                        './preceding-sibling::li[1]/a/text()').extract_first()
                    item['categoria'] = response.css('li.subCategoryName::text')\
                        .extract_first()
                    item['descripcion'] = descripcion
                    item['precio'] = producto.css('span.price ::text')\
                        .extract_first()
                    item['precioPrevio'] = producto.css('strike ::text')\
                        .extract_first()
                    item['precioOferta'] = producto.css('span.price-less ::text')\
                        .extract_first()
                    # Se captura el primer match del regex
                    item['precioMedida'] = producto.css('p.format-price::text')\
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
            except Exception as e:
                raise ValueError("ERROR parseando el producto {}.\n{}"
                                 .format(descripcion, e))
