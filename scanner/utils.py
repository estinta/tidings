from datetime import datetime, timedelta

from . import Finviz
from . import StockLookup
from . import StockNews

from .models import News, Stock

def fetch_news(force=False, user=None, tickers=None):
    qs = Stock.objects.all()
    if user:
        qs = qs.filter(user=user)
    if tickers != None:
        qs = qs.filter(ticker__in=tickers)
    qs = qs.values_list('ticker', flat=True).distinct()
    for ticker in qs:
        try:
            latest_news = News.objects.filter(ticker=ticker).latest('created')
        except News.DoesNotExist:
            latest_news = None
        if force or latest_news is None \
                or latest_news.created + timedelta(hours=3) < datetime.utcnow():
            for source, news_items in StockNews.get_news(ticker).items():
                for item in news_items:
                    if News.objects.filter(ticker=ticker, source=source,
                            guid=item['guid']).exists():
                        continue
                    news = News()
                    news.ticker = ticker
                    news.source = source
                    for key, value in item.items():
                        # description, title, link, pub_date
                        news.__setattr__(key, value)
                    news.save()

def fetch_ibd(username, password, force=False, user=None,
        tickers=None):
    qs = Stock.objects.all()
    if user is not None:
        qs = qs.filter(user=user)
    if tickers != None:
        qs = qs.filter(ticker__in=tickers)
    if not force:
        old_date = datetime.utcnow() - timedelta(hours=24)
        qs = qs.filter(last_update__lt=old_date)
    if len(qs) > 0:
        if not StockLookup.login(username, password):
            # we failed to login
            print "Login failed, can't update IBD data"
            return
    for stock in qs:
        try:
            response = StockLookup.get_stock(stock.ticker)
            stock_dict = StockLookup.parse_stock(response)
        except Exception, e:
            print "could not fetch IBD data", e
            continue
        if not response or not stock_dict:
            continue
        stock.ibd_industry_rank = stock_dict['industry_group_rank']
        stock.ibd_earnings_due_date = stock_dict['earnings_due_date']
        stock.company_name = stock_dict['company_name']
        stock.ibd_industry_group = stock_dict['industry_group']
        stock.ibd_earnings_percentage_lastquarter = stock_dict[
                'eps_perc_change']
        stock.ibd_sales_percentage_lastquarter = stock_dict[
                'sales_perc_change']
        stock.ibd_eps_rank = stock_dict['eps_rating']
        # lump this in here too; it all uses the same last_update date
        stock.float = Finviz.get_float(stock.ticker)
        stock.last_update = datetime.utcnow()
        stock.save()

