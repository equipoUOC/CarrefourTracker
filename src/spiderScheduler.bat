:: Se activa el entorno anaconda
call C:\Users\{Usuario}\anaconda3\Scripts\activate.bat "C:\Users\{Usuario}\anaconda3\envs\{nombreEntorno}"

:: Se dirige al directorio donde se encuentra el script
call cd "{pathRepositorioLocal}\CarrefourTracker\src\"

:: Se inicia la araña
call scrapy crawl carrefourSpider