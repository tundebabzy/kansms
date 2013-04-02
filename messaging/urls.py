from django.conf.urls import patterns, include, url

from messaging.views import (SendSmsWizard, skip_if_single_receipient,
skip_if_bulk_receipient, initial_data_for_wizard, SavedDraftListView,
VerifyView, ResendSuccessView, NumberListView, HomePageView)

from messaging.forms import MessageForm, SingleReceipientForm, BulkReceipientForm

compose_forms = [MessageForm, SingleReceipientForm, BulkReceipientForm]



urlpatterns = patterns('',
    url(r'^$', HomePageView.as_view(), name='home'),
    
    url(r'^send/$', SendSmsWizard.as_view(compose_forms,
        condition_dict={'1': skip_if_single_receipient, '2': skip_if_bulk_receipient}),
        name='send'),

    url(r'^send/(?P<msg_id>\d+)/$', SendSmsWizard.as_view(compose_forms,
        condition_dict={'1': skip_if_single_receipient, '2': skip_if_bulk_receipient},
        initial_dict={'0':initial_data_for_wizard}), name='send_to_others'),

    url(r'^sent/$', SavedDraftListView.as_view(), name='all_sent'),

    url(r'^resend/(?P<msg_id>\d+)/$', VerifyView.as_view(), name='resend'),

    url(r'^resend/success/$', ResendSuccessView.as_view(), name='resend_success'),

    url(r'^receipients/(?P<msg_id>\d+)/$', NumberListView.as_view(), name='receipients'),
)
