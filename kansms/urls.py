from django.conf.urls import patterns, include, url

from django.contrib.auth.views import (logout_then_login, login,
password_reset, password_reset_done, password_reset_confirm,
password_reset_complete)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from messaging.views import HelpPageView
from messaging.api import SmsResource

from accounts import views as account_views

from userena import views as userena_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()
sms_resource = SmsResource()


urlpatterns = patterns('',
    url(r'^api/', include(sms_resource.urls)),
    
    url(r'^$', include('messaging.urls')),

    url(r'^message/', include('messaging.urls')),

    # These url pattern should be handled by userena but i'm gonna
    # intercept it and link it to my slightly modified view
    url(r'^accounts/(?P<username>[\.\w-]+)/edit/$',
       account_views.profile_edit,
       name='userena_profile_edit'),

    # These patterns will display the saved user profiles and that is a
    # No NO so I will intercept and make return 404
    url(r'^accounts/page/(?P<page>[0-9]+)/$',
       account_views.not_allowed,
       name='userena_profile_list_paginated'),
    url(r'^accounts/$',
       account_views.not_allowed,
       name='userena_profile_list'),

    url(r'^accounts/', include('userena.urls')),

    url(r'^help/$', HelpPageView.as_view(), name='help'),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
