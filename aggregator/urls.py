from django.conf.urls.defaults import *

urlpatterns = patterns('aggregator.views',
        url(r'^$', 'aggregator', name='aggregator'),
        url(r'^post_tweet/$', 'post_tweet', name='post_tweet'),
        url(r'^refresh/$', 'refresh_aggregates', name="refresh_aggregates"),
)
