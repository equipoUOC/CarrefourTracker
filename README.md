# CarrefourTracker

Esta aplicación es un rastreador de precios que recorre la web del supermercado carrefour
capturando la información relevante sobre los productos de forma que una vez se disponga
de datos de varios días se puedan comparar los precios.

Para utilizar este script es recomendable utilizar las siguientes  instrucciones:

	1. Crear un nuevo entorno conda para instalar los paquetes de forma independiente al sistema:
			"conda create -n {nombreEntorno}"
	2. Activar el entorno: "conda activate {nombreEntorno}"
	3. Instalar scrapy: "conda install -c conda-forge scrapy"
	4. Ir al directorio src
	5. Instalar los demás requerimientos: "pip install -r requirements.txt"
	6. Ejecutar el programa: "scrapy crawl carrefourSpider -o ../CSVdata/CarrefourDailyPricing_05112020_2340.csv"
