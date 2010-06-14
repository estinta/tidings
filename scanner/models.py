from django.db import models

class Stock(models.Model):
    ticker = models.CharField(max_length=15)
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
    telechart = models.CharField(max_length=15, blank=True, default="")
    neglect = models.CharField(max_length=363, blank=True, default="")
    comment = models.CharField(max_length=563, blank=True, default="")
    ep_type = models.CharField(max_length=63, blank=True, default="")
    action = models.CharField(max_length=63, blank=True, default="")
    risk_percentage = models.CharField(max_length=63, blank=True, default="")

class News(models.Model):
    stock = models.ForeignKey(Stock)
    source = models.CharField(max_length=15)
    title = models.CharField(max_length=128)
    description = models.TextField()
    link = models.URLField()
    pub_date = models.CharField(max_length=10)

