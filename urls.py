from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

import os.path

admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),

    (r'^$', 'reporter.views.index'),
    (r'^remove/(?P<symbol>[^/]+)/$', 'reporter.views.remove_symbol'),
    (r'^removeall/$', 'reporter.views.remove_all_symbols'),
    (r'^purgedb/$', 'reporter.views.purge_db'),

    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG == True:
    urlpatterns += patterns('',
        (r'^static/(.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(settings.PROJECT_HOME, 'static')}))
