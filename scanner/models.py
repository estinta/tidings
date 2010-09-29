from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from . import StockNews

class UserProfile(models.Model):
    # Required to be a valid profile module
    user = models.ForeignKey(User, unique=True)
    # Start of our tracked fields
    ibd_user = models.CharField("IBD Username", max_length=100,
            blank=True, default="")
    ibd_password = models.CharField("IBD Password", max_length=100,
            blank=True, default="")
    briefing_user = models.CharField("Briefing.com Username", max_length=100,
            blank=True, default="")
    briefing_password = models.CharField("Briefing.com Password", max_length=100,
            blank=True, default="")

def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.create(user=kwargs.get('instance'))

post_save.connect(ensure_profile_exists, sender=User)

def get_news_sources():
    l = StockNews.get_sources()
    l.sort()
    return l

class Stock(models.Model):
    ticker = models.CharField(max_length=15)
    user = models.ForeignKey(User, db_index=True)

    ## IBD Data
    # TODO: we can probably find company name somewhere else than IBD...
    company_name = models.CharField(max_length=127, blank=True, default="")
    ibd_earnings_due_date = models.CharField(max_length=15,
            blank=True, default="")
    ibd_industry_group = models.CharField(max_length=127, blank=True, default="")
    ibd_industry_rank = models.CharField(max_length=15,
            blank=True, default="")
    ibd_earnings_percentage_lastquarter = models.CharField(max_length=15,
            blank=True, default="")
    ibd_sales_percentage_lastquarter = models.CharField(max_length=15,
            blank=True, default="")
    ibd_eps_rank = models.CharField(max_length=15, blank=True, default="")
    ibd_last_update = models.DateTimeField(default=datetime(2000, 1, 1))

    ## Finviz Data
    finviz_float = models.CharField(max_length=15, blank=True, default="")
    finviz_last_update = models.DateTimeField(default=datetime(2000, 1, 1))

    ## News Data
    yahoo_last_update = models.DateTimeField(default=datetime(2000, 1, 1))
    google_last_update = models.DateTimeField(default=datetime(2000, 1, 1))
    msn_last_update = models.DateTimeField(default=datetime(2000, 1, 1))
    briefing_last_update = models.DateTimeField(default=datetime(2000, 1, 1))

    def current_news(self):
        '''returns list of (source, [ news ]) tuples'''
        news = []
        for source in get_news_sources():
            news.append((source, News.objects.filter(ticker=self.ticker,source=source).order_by('-pub_date')[:20]))
        return news

class News(models.Model):
    # related to stocks, but not a true foreign key
    ticker = models.CharField(max_length=15, db_index=True)
    source = models.CharField(max_length=15)
    title = models.CharField(max_length=512)
    description = models.TextField()
    link = models.URLField(max_length=512)
    pub_date = models.DateTimeField()
    created = models.DateTimeField(default=datetime.utcnow)
    guid = models.CharField(max_length=240)

    class Meta:
		# I hate you, MySQL. These can't add up to more than 1000 bytes using
		# MyISAM, and since UTF-8 takes 3 bytes a piece, that means 333
		# characters total for all three fields, thus the oddly sized '240'
		# used for guid above.
        unique_together = ('source', 'ticker', 'guid')

        # Another useful index that is great to have, but we can't create it
        # via Django due to its non-uniqueness:
        # CREATE INDEX `scanner_news_published` ON `scanner_news` (`source`, `ticker`, `pub_date`);
