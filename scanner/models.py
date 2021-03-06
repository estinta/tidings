from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

class UserProfile(models.Model):
    # Required to be a valid profile module
    user = models.ForeignKey(User, unique=True)
    # Start of our tracked fields
    ibd_user = models.CharField("IBD Username", max_length=100,
            blank=True, default="")
    ibd_password = models.CharField("IBD Password", max_length=100,
            blank=True, default="")
    ibd_valid = models.NullBooleanField("IBD Credentials Valid",
            editable=False, default=None)
    briefing_user = models.CharField("Briefing.com Username", max_length=100,
            blank=True, default="")
    briefing_password = models.CharField("Briefing.com Password", max_length=100,
            blank=True, default="")
    briefing_valid = models.NullBooleanField("Briefing.com Credentials Valid",
            editable=False, default=None)

def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.create(user=kwargs.get('instance'))

post_save.connect(ensure_profile_exists, sender=User)

class Stock(models.Model):
    ticker = models.CharField(max_length=15)

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

    def yahoo_news(self):
        return News.objects.filter(stock=self,source='yahoo').order_by('-pub_date')[:20]

    def google_news(self):
        # Google always has longer descriptions, so fetch fewer of them
        return News.objects.filter(stock=self,source='google').order_by('-pub_date')[:15]

    def briefing_news(self):
        return News.objects.filter(stock=self,source='briefing').order_by('-pub_date')[:20]

class News(models.Model):
    stock = models.ForeignKey(Stock, null=True)
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
        unique_together = ('source', 'stock', 'guid')

        # Another useful index that is great to have, but we can't create it
        # via Django due to its non-uniqueness:
        # CREATE INDEX `scanner_news_published` ON `scanner_news` (`source`, `stock_id`, `pub_date`);
# vim: set ts=4 sw=4 et:
