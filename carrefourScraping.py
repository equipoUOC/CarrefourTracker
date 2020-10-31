import datetime
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess

class CarrefourItem(scrapy.Item):
    seccion = scrapy.Field()
    categoria = scrapy.Field()
    descripcion = scrapy.Field()
    precio_Kg = scrapy.Field()
    precio = scrapy.Field()
    precioPrevio = scrapy.Field()
    precioOferta = scrapy.Field()
    promocion = scrapy.Field()
    enlace = scrapy.Field()

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
        # Extraemos el código html correspodiente a cada sección
        listaSecciones = response.css('li.level2-item')
        # print("Se han encontrado {} secciones.".format(len(listaSecciones)))
        # Para cada sección, seguimos el enlace hacia las diferentes categorías
        for seccion in listaSecciones:
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
                                  headers=headers,
                                  cb_kwargs={'seccion': nombreSeccion})

    def parse_categoria(self, response, seccion):
        # Extraemos el código html de las diferentes categorias
        listaCategorias = response.css('div.category')
        # print("Se han encontrado {} categorias.".format(len(listaCategorias)))
        for categoria in listaCategorias:
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
                                  headers=headers,
                                  cb_kwargs={'seccion':seccion,
                                             'categoria': nombreCategoria})

    def parse_productos(self, response, seccion, categoria):
        # Se filtran los "product-card-item" para no mezclar precios
        items_producto = response.css('article.product-card-item')
        # print("Se han encontrado {} productos".format(len(items_producto)-1))
        # Se recorre cada item para extraer el nombre, los precios y las
        # ofertas
        for producto in items_producto:
            descripcion = producto.css('p.title-product ::text')\
                .extract_first()
            # Si hay descripción asignamos los valores, sino se comprueba si
            # hay página siguiente
            if(descripcion):
                item = CarrefourItem()
                # Buscamos los nombres del producto
                item['seccion'] = seccion
                item['categoria'] = categoria
                item['descripcion'] = descripcion
                item['precio'] = producto.css('span.price ::text')\
                    .extract_first()
                item['precioPrevio'] = producto.css('strike ::text')\
                    .extract_first()
                item['precioOferta'] = producto.css('span.price-less ::text')\
                    .extract_first()
                item['precio_Kg'] = producto.css('p.format-price ::text')\
                    .extract_first()
                item['promocion'] = producto.css('p.promocion-copy ::text')\
                    .extract_first()
                link = producto.css('a.js-gap-product-click-super ::attr(href)')\
                    .extract_first()
                item['enlace'] = response.urljoin(link)
                # Se añade a la lista un diccionario con los valores capturados
                lista_productos.append({'Seccion':item['seccion'],
                                        'Categoria':item['categoria'],
                                        'Descripcion':item['descripcion'],
                                        'Precio/Kg':item['precio_Kg'],
                                        'Precio':item['precio'],
                                        'PrecioPrevio':item['precioPrevio'],
                                        'Ofertas':item['precioOferta'],
                                        'Promociones':item['promocion'],
                                        'Enlace':item['enlace']})
            else:
                # Extraemos información de las páginas siguientes de la
                # misma categoria
                next_page_url = response.css('a.next::attr(href)')\
                    .extract_first()
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

    fecha = '{0:%d%m%Y_%H%M}'.format(datetime.datetime.now())
    fileName = 'CarrefourDailyPricing_' + fecha + '.csv'
    filePath = './CSVdata/' + fileName
    # Si hay productos en la lista se crea un fichero con los datos
    if lista_productos:
        # Se crea un dataframe con todos los valores y se guarda como CSV
        productos = pd.DataFrame(lista_productos)
        productos.to_csv(filePath, columns=['Seccion', 'Categoria',
                                            'Descripcion', 'Precio/Kg',
                                            'Precio', 'PrecioPrevio',
                                            'Ofertas', 'Promociones',
                                            'Enlace'],
                         encoding='utf-8-sig')
