from django.db import models
from django.forms import ModelForm
from .models import UserProfile

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)
# vim: set ts=4 sw=4 et:
