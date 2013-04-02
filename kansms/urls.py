from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout_then_login, login, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from messaging.views import (SendSmsWizard, skip_if_single_receipient,
skip_if_bulk_receipient, initial_data_for_wizard, SavedDraftListView,
HelpPageView, VerifyView, ResendSuccessView, NumberListView, HomePageView)
from messaging.forms import MessageForm, SingleReceipientForm, BulkReceipientForm
from messaging.api import SmsResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
sms_resource = SmsResource()

compose_forms = [MessageForm, SingleReceipientForm, BulkReceipientForm]

urlpatterns = patterns('',
    url(r'^api/', include(sms_resource.urls)),
    url(r'^dash/$', HomePageView.as_view(), name='home'),
    url(r'^dash/message/send/$', SendSmsWizard.as_view(compose_forms,
                        condition_dict={'1': skip_if_single_receipient,
                                        '2': skip_if_bulk_receipient}),
                    name='send'),
    url(r'^dash/message/send/(?P<msg_id>\d+)/$', SendSmsWizard.as_view(compose_forms,
                        condition_dict={'1': skip_if_single_receipient,
                                        '2': skip_if_bulk_receipient},
                        initial_dict={'0':initial_data_for_wizard,
                                      '1':{'single_receipient':'08058008000'}}),
                        name='send_to_others'),
    url(r'^dash/sent/$', SavedDraftListView.as_view(),
                            name='all_sent'
        ),
    url(r'^dash/resend/(?P<msg_id>\d+)/$', VerifyView.as_view(), name='resend'
        ),
    url(r'^dash/resend/success/$', ResendSuccessView.as_view(), name='resend_success'
        ),
    url(r'^dash/receipients/(?P<msg_id>\d+)/$', NumberListView.as_view(),
                                name='receipients'
        ),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            password_reset_confirm, name='password_reset_confirm'),
    url(r'^accounts/reset/$', password_reset,
            {'post_reset_redirect': '/accounts/reset-done/'}, name='password_reset',
        ),
    url(r'^accounts/reset-done/$', password_reset_done, name='password_reset_done'),
    url(r'^accounts/complete-reset/$', password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/login/$', login, name='login'
        ),
    url(r'^accounts/logout/$', logout_then_login,
            {'login_url': '/accounts/login/'}, name='logout-then-login',
        ),
    url(r'^help/$', HelpPageView.as_view(), name='help'),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
