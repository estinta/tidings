from django.views.decorators.http import require_POST
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.views.generic.list_detail import object_list
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.flatpages.models import FlatPage

from aggregator.models import Tweet
from aggregator.forms import TweetForm

@login_required
def aggregator(request):
    '''Aggregate several objects into a single feed.'''
    tweet_form = TweetForm()
    return render_aggregates(request, template="aggregates/aggregates.html",
            extra_context={'form': tweet_form})

@login_required
def post_tweet(request):
    form = TweetForm(request.POST or None)
    if form.is_valid():
        tweet = form.save(commit=False)
        tweet.user = request.user
        tweet.save()
        return redirect(reverse('aggregator'))

    return render_to_response('aggregates/tweet_form.html',
            RequestContext(request, {
                'form': form}))

@login_required
def refresh_aggregates(request, num_tweets=20,
        template="aggregates/aggregate_list.html", extra_context=None):
    return render_aggregates(request, num_tweets, template, extra_context)

def render_aggregates(request, num_tweets=20,
        template="aggregates/aggregate_list.html", extra_context=None):
    extra_context = extra_context or {}

    num_tweets = int(num_tweets)
    if num_tweets > 200:
        num_tweets = 200

    tweets = Tweet.objects.all().order_by("-time")[:num_tweets]

    context = {'aggregates': tweets}
    context.update(extra_context)

    return render_to_response(template, RequestContext(request, context))

# vim: set ts=4 sw=4 et:
