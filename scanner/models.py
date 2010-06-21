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

def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.create(user=kwargs.get('instance'))

post_save.connect(ensure_profile_exists, sender=User)

class Stock(models.Model):
    ticker = models.CharField(max_length=15)
    user = models.ForeignKey(User, db_index=True)
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
    float = models.CharField(max_length=15, blank=True, default="")
    last_update = models.DateTimeField(default=datetime(2000, 1, 1))

    @property
    def news_set(self):
        return News.objects.filter(ticker=self.ticker).order_by('source', '-pub_date')

class News(models.Model):
    # related to stocks, but not a true foreign key
    ticker = models.CharField(max_length=15, db_index=True)
    source = models.CharField(max_length=15)
    title = models.CharField(max_length=512)
    description = models.TextField()
    link = models.URLField(max_length=512)
    pub_date = models.DateTimeField()
    created = models.DateTimeField(default=datetime.utcnow)

