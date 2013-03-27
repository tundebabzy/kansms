from django.conf.urls import patterns, include, url

urlpatterns = patterns('messaging.views',
    url(r'^$', 'main_dash'),
    url(r'^inbox/$', 'get_inbox', name='inbox'),
)
