from django import forms

from aggregator.models import Tweet


class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ("message",)
