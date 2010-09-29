from django.db import models
from django.contrib.auth.models import User

class Tweet(models.Model):
    user = models.ForeignKey(User)
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True, db_index=True)
# vim: set ts=4 sw=4 et:
