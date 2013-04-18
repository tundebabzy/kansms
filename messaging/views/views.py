import re
import itertools

from django.views.generic import TemplateView
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from messaging.sender import SmsBlaster

from messaging.models import Contact, Sms, List

from backends.api import send_bulk_sms

class OrdinaryView(TemplateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrdinaryView, self).dispatch(*args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super(OrdinaryView, self).get_context_data(**kwargs)
        user = self.request.user
        user_balance = user.profile.get_balance()
        context.update({'credits': user_balance,})
        return context

class HomePageView(OrdinaryView):
    template_name = 'home.html'

class HelpPageView(OrdinaryView):
    template_name = 'help.html'

class ResendSuccessView(OrdinaryView):
    template_name = 'resend_success.html'

class NumberListView(OrdinaryView):
    template_name = 'receipients.html'

    def get_context_data(self, **kwargs):
        msg_id = self.kwargs.get('msg_id', None)
        context = super(NumberListView, self).get_context_data(**kwargs)
        message = Sms.objects.get(pk=msg_id)
        phone_numbers = List.objects.filter(message__id=msg_id, message__sender=self.request.user).values_list('number', flat=True)
        context.update({'message':message,'phone_numbers':phone_numbers})

        return context
        
class VerifyView(OrdinaryView):
    template_name = 'confirm_resend.html'

    def get_context_data(self, **kwargs):
        msg_id = self.kwargs.get('msg_id', None)
        context = super(VerifyView, self).get_context_data(**kwargs)
        # Also make sure that the messages belong to the logged in user
        phone_numbers = List.objects.filter(message__id=msg_id, message__sender=self.request.user).values_list('number', flat=True)
        context.update({'phone_numbers':phone_numbers, 'msg_id':msg_id})
        return context 

    def post(self, request, *args, **kwargs):
        # VERY UGLY.....
        # Lets start trying to sanitize form input
        
        post_data = self.request.POST

        msg_id = post_data.get('message', None)
        if not msg_id:
            return self.get(request, *args, **kwargs)
        
        s = post_data.getlist('selected', None)
        if s:
            selected = self.clean_selected(s)
        else:
            return self.get(request, *args, **kwargs)

        p = post_data.get('post', False)
        to_post = p == 'yes'
        if not to_post:
            return self.get(request, *args, **kwargs)

        d = post_data.get('action', None)
        send_selected = d == 'send_selected'
        if not send_selected:
            return self.get(request, *args, **kwargs)

        if msg_id and selected and to_post and send_selected:
            numbers = selected
            if len(numbers) != len(selected):
                return self.get(request, *args, **kwargs)
            message = Sms.objects.filter(pk=msg_id).values_list('body', 'sender_alias')
            if not message:
                return self.get(request, *args, **kwargs)
            sms_pack = SmsBlaster(text=message[0][0], numbers=selected, user_profile=self.request.user.get_profile(), sent_by=message[0][1])
            sms_pack_data = sms_pack.blast()

            data = {'num_sent': sms_pack_data['successful'] + sms_pack_data['failed'],
                    'num_successful':sms_pack_data['successful'],
                    'num_failed': sms_pack_data['failed']
            }
            return HttpResponseRedirect(reverse('all_sent'))
            
    def clean_selected(self, value):
        if not isinstance(value, list):
            # arguement should be a list
            return []
        acceptable = re.compile('^234[0-9]{10}$')
        verified = []
        
        for el in value:
            temp = acceptable.search(el)
            if temp:
                verified.append(el)
            else:
                # bail if theres any crap value
                verified = []
                return verified
        return verified
