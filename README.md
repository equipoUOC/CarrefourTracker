# CarrefourTracker

En el presente proyecto, hemos construido un web crawler capaz de navegar por la web del supermercado [Carrefour](https://www.carrefour.es/supermercado/) y extraer datos de los diferentes productos.

Para utilizar este script es necesario seguir los siguientes pasos:

	1. Instalar Anaconda en nuestro equipo
	2. Crear un nuevo entorno conda para instalar los paquetes de forma independiente al sistema:
			"conda create -n {nombreEntorno}"
	3. Activar el entorno: "conda activate {nombreEntorno}"
	4. Instalar scrapy: "conda install -c conda-forge scrapy"
	5. Clonar este repositorio e ir al directorio src
	7. Ejecutar el programa: "scrapy crawl carrefourSpider"

Para planificar un raspado cada día a las 08:00AM, se configura el programador de tareas de windows para ejecutar el script [spiderScheduler](src/spiderScheduler.bat), configurando previamente el usuario, el nombre del entorno y el path del equipo donde se ejecutará.
