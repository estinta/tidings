from datetime import datetime, timedelta

from . import Finviz
from . import StockLookup
from . import StockNews

from .models import News, Stock

def fetch_news(force=False, user=None, tickers=None):
    qs = Stock.objects.all()
    if tickers != None:
        qs = qs.filter(ticker__in=tickers)

    old_date = datetime.utcnow() - timedelta(minutes=15)
    # Slightly hacky, but MySQL silently truncates our values otherwise
    # so we lose. This ensures we can do equality matching without any
    # problems.
    guid_len = News._meta.get_field('guid').max_length

    for stock in qs:
        news_items = []
        if force or stock.yahoo_last_update < old_date:
            news_items.extend(StockNews.get_news(stock.ticker, 'yahoo'))
            stock.yahoo_last_update = datetime.utcnow()
        if force or stock.google_last_update < old_date:
            news_items.extend(StockNews.get_news(stock.ticker, 'google'))
            stock.google_last_update = datetime.utcnow()
        if force or stock.msn_last_update < old_date:
            news_items.extend(StockNews.get_news(stock.ticker, 'msn'))
            stock.msn_last_update = datetime.utcnow()

        for item in news_items:
            guid = item['guid'][:guid_len]
            if News.objects.filter(stock=stock,
                    source=item['source'], guid=guid).exists():
                continue
            news = News()
            news.stock = stock
            for key, value in item.items():
                # description, title, link, pub_date, source, guid (overridden below)
                news.__setattr__(key, value)
            news.guid = guid
            news.save()

        stock.save()

def fetch_ibd(username, password, force=False,
        tickers=None):
    qs = Stock.objects.all()
    if tickers != None:
        qs = qs.filter(ticker__in=tickers)
    if not force:
        old_date = datetime.utcnow() - timedelta(hours=1)
        qs = qs.filter(ibd_last_update__lt=old_date)
    if len(qs) > 0:
        if not username or not password or \
                not StockLookup.login(username, password):
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
        stock.ibd_last_update = datetime.utcnow()
        stock.save()

def fetch_finviz(force=False, tickers=None):
    qs = Stock.objects.all()
    if tickers != None:
        qs = qs.filter(ticker__in=tickers)
    if not force:
        old_date = datetime.utcnow() - timedelta(hours=24)
        qs = qs.filter(finviz_last_update__lt=old_date)
    for stock in qs:
        stock.finviz_float = Finviz.get_float(stock.ticker)
        stock.finviz_last_update = datetime.utcnow()
        stock.save()

def validate_credentials(profile, save=True):
    if not profile.ibd_user or not profile.ibd_password:
        success = None
    else:
        success = StockLookup.login(profile.ibd_user, profile.ibd_password)
    profile.ibd_valid = success

    if not profile.briefing_user or not profile.briefing_password:
        success = None
    else:
        success = None
    profile.briefing_valid = success

    if save:
        profile.save()

    return profile

# vim: set ts=4 sw=4 et:
