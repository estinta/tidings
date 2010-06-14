from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

import os.path

admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG == True:
    urlpatterns += patterns('',
        (r'^static/(.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(settings.PROJECT_HOME, 'static')}))
