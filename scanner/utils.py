from . import Finviz
from . import StockLookup
from . import StockNews

from .models import News, Stock

def fetch_news():
    for stock in Stock.objects.filter(news__isnull=True):
        print stock.ticker
        for source, news_items in StockNews.get_news(stock.ticker).items():
            for item in news_items:
                news = News()
                news.stock = stock
                news.source = source
                for key, value in item.items():
                    # description, title, link, pub_date
                    news.__setattr__(key, value)
                news.save()

def fetch_ibd():
    qs = Stock.objects.filter(ibd_industry_rank='')
    if len(qs) > 0:
        StockLookup.login()
    for stock in qs:
        print stock.ticker
        response = StockLookup.get_stock(stock.ticker)
        try:
            stock_dict = StockLookup.parse_stock(response)
        except Exception, e:
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
        stock.save()

def fetch_float():
    for stock in Stock.objects.filter(float=''):
        stock.float = Finviz.get_float(stock.ticker)
        stock.save()

