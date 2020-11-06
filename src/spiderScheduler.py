import datetime as dt
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from PriceTracker.spiders.carrefour_spider import CarrefourSpider

def crawl_job():
    """
    Inicia las arañas y devuelve un Deferred cuando se ha completado el proceso.
    """
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    return runner.crawl(CarrefourSpider)

def temporizador(null, segundos):
    """
    Espera el tiempo indicado hasta el siguiente raspado
    """
    print("Temporizador iniciado a las {}".format(dt.datetime.now()))
    reactor.callLater(segundos, crawl)

def schedule_next_crawl(null, hour, minute):
    """
    Programamos el siguiente raspado
    """
    print("Configura la hora del siguiente raspado")
    mañana = (
        dt.datetime.now() + dt.timedelta(days=1)
        ).replace(hour=hour, minute=minute, second=0, microsecond=0)
    sleep_time = (mañana - dt.datetime.now()).total_seconds()
    reactor.callLater(sleep_time, crawl)

def crawl():
    """
    Una función recursiva que programa los raspados
    """
    # crawl_job() devuelve un Deferred
    d = crawl_job()
    # Programa el raspado para cada día a la hora indicada
    d.addCallback(schedule_next_crawl, hour=08, minute=00)
    # Programa una espera de los segundos indicados hasta el siguiente raspado
    # d.addCallback(temporizador, 30)
    d.addErrback(catch_error)

def catch_error(failure):
    print(failure.value)

if __name__=="__main__":
    crawl()
    reactor.run()