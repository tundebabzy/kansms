from django.conf.urls import patterns, include, url

from django.contrib.auth.views import (logout_then_login, login,
password_reset, password_reset_done, password_reset_confirm,
password_reset_complete)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from messaging.views import HelpPageView

from messaging.api import SmsResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()
sms_resource = SmsResource()


urlpatterns = patterns('',
    url(r'^api/', include(sms_resource.urls)),
    
    url(r'^$', include('messaging.urls')),

    url(r'^message/', include('messaging.urls')),

    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            password_reset_confirm, name='password_reset_confirm'),

    url(r'^accounts/reset/$', password_reset,
            {'post_reset_redirect': '/accounts/reset-done/'}, name='password_reset',),

    url(r'^accounts/reset-done/$', password_reset_done, name='password_reset_done'),

    url(r'^accounts/complete-reset/$', password_reset_complete, name='password_reset_complete'),

    url(r'^accounts/login/$', login, name='login'),

    url(r'^accounts/logout/$', logout_then_login,
            {'login_url': '/accounts/login/'}, name='logout-then-login'),

    url(r'^help/$', HelpPageView.as_view(), name='help'),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
