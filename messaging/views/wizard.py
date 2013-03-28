from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from messaging.forms import MessageFormError
from messaging.models import Sms
from messaging.sender import SmsBlaster

class SendSmsWizard(SessionWizardView):
    """    
    Form wizard. It is made up of three forms;
    
    Form 1. Collect the message to be sent and if the user would like to
            send the message to a single number, multiple numbers or
            choose from his phone book.
    Form 2. Form to collect single phone number
    Form 3. Form to collect multiple phone numbers
    Form 4. Form for user to select from stored contacts.

    """
    template_name = 'dash.html'
    

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SendSmsWizard, self).dispatch(*args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super(SendSmsWizard,self).get_context_data(form, **kwargs)
        user = self.request.user
        #user_balance = user.get_profile().get_balance()
        user_balance = '100'    # This line is temporary
            
        context.update({'user':user, 'credits':user_balance})
        return context

    def get_form_kwargs(self, step=None):
        """
        This is the method where arguments to be added to the form(s) to
        be initialised can be set. The default implementation simply
        returns an empty dictionary and is updated with arguments by the
        get_form method.
        """
        if step == '3':
            return {'error_class': MessageFormError, 'owner':self.request.user}
        return {'error_class': MessageFormError}

    def get_form_initial(self, step):
        """
        Overriden to cache the initial_dict function (if provided). This
        reduces database hits when the function is an ORM function.
        """
        self.initial = initial = getattr(self, 'initial', {})
        if not initial.get(step, None):
            initial[step] = self.initial_dict.get(step)
            if callable(initial[step]):
                # Call the function by passing the current instance
                self.initial[step] = initial[step](self)
        return initial[step]

    def done(self, form_list, **kwargs):
        form_one_data, form_two_data = [form.cleaned_data for form in form_list]
        
        text = form_one_data['message']
        sender_name = form_one_data['sender']
        to = form_two_data.get('single_receipient',None) or form_two_data.get('bulk_receipient', None)

        sms_pack = SmsBlaster(text=text,numbers=to, user=self.request.user, sent_by=sender_name)
        sms_pack_data = sms_pack.blast()
                                
        return render_to_response('done.html', {
            'failed': sms_pack_data['failed'],
            'message': sms_pack_data['text'],
            'draft': sms_pack_data['sms_instance'],
            'successful': sms_pack_data['successful']
        }, context_instance=RequestContext(self.request))

# Condition_dicts for Form Wizard
def skip_if_single_receipient(wizard):
    """
    Makes the wizard skip the second form if the user indicates in the
    first form that the method for entering phone numbers is 'Single
    Receipient'
    """
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    method = cleaned_data.get('method', False)
    return method == 'SR'

def skip_if_bulk_receipient(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    method = cleaned_data.get('method', False)
    return method == 'BR'
    
def initial_data_for_wizard(wizard):
    """
    This tries to query the database for a Sms object and returns a
    dictionary that will be used as the initial_dict for our SendSmsWizard
    when loading a Sms object.
    """
    msg_id = wizard.kwargs.get('msg_id', None)
    if msg_id:
        try:
            message = Sms.objects.filter(pk=msg_id, sender=wizard.request.user).values_list('body', flat=True)[0]
            return {'message': message }
        except:
            return {'message': ''}
