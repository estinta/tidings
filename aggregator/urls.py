from django.conf.urls.defaults import *

urlpatterns = patterns('aggregator.views',
        url(r'^$', 'aggregator', name='aggregator'),
        url(r'^post_tweet/$', 'post_tweet', name='post_tweet'),
        url(r'^refresh/(?P<num_tweets>\d+)/$', 'refresh_aggregates',
            name="refresh_aggregates"),
        url(r'^refresh/$', 'refresh_aggregates'),
)
# vim: set ts=4 sw=4 et:
