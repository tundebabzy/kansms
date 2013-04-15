from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from messaging.forms import MessageFormError
from messaging.models import Sms
from messaging.sender import SmsBlaster
from django.core.files.storage import FileSystemStorage

class SendSmsWizard(SessionWizardView):
    template_name = 'dash.html'
    file_storage = FileSystemStorage()
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SendSmsWizard, self).dispatch(*args, **kwargs)

    def get_context_data(self, form, **kwargs):
        """ Adds data to the default context """
        context = super(SendSmsWizard,self).get_context_data(form, **kwargs)
        user = self.request.user
        #user_balance = user.get_profile().get_balance()
        user_balance = '100'    # This line is temporary
            
        context.update({'user':user, 'credits':user_balance})
        return context

    def get_form_kwargs(self, step=None):
        """ updates the wizard's kwarg """
        if step == '4':
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

    def get_form_step_files(self, form):
        """ Make sure uploaded files are in text/plain format """
        # TODO: Better file format verification
        file_dict = form.files
        if file_dict:
            for key in file_dict:
                if file_dict[key].content_type != 'text/plain':
                    form.files = {}
                    
        return form.files

    def done(self, form_list, **kwargs):
        form_one_data, form_two_data = [form.cleaned_data for form in form_list]
        
        text = form_one_data['message']
        sender_name = form_one_data['sender']
        
        files = form_two_data.get('file_name', None)
        if files and files.content_type == 'text/plain':
            file_data = []
            for chunk in files.chunks():
                file_data.extend(chunk.strip().split('\n'))
        
        to = form_two_data.get('single_receipient',None) or form_two_data.get('bulk_receipient', None) or file_data

        sms_pack = SmsBlaster(text=text, numbers=to, user=self.request.user, sent_by=sender_name)
        sms_pack_data = sms_pack.blast()
                                
        return render_to_response('done.html', {
            'failed': sms_pack_data['failed'],
            'message': sms_pack_data['text'],
            'draft': sms_pack_data['sms_instance'],
            'successful': sms_pack_data['successful']
        }, context_instance=RequestContext(self.request))

# Condition_dicts for Form Wizard
def get_selected_method(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('method', False)

def skip_if_single_receipient(wizard):
    """
    Makes the wizard skip all other forms except SingleReceipientForm
    """
    return get_selected_method(wizard) == 'SR'

def skip_if_bulk_receipient(wizard):
    """
    Makes the wizard skip all other forms except BulkReceipientForm
    """
    return get_selected_method(wizard) == 'BR'

def is_file_load(wizard):
    """
    Makes the wizard skip all other forms except FileUploadForm
    """
    return get_selected_method(wizard) == 'FU'
    
def initial_data_for_wizard(wizard):
    """
    Takes an Sms object id which if exists in the database will be used
    as initial data for form wizard MessageForm.
    """
    msg_id = wizard.kwargs.get('msg_id', None)
    if msg_id:
        try:
            message = Sms.objects.filter(pk=msg_id, sender=wizard.request.user).values_list('body', flat=True)[0]
        except:
            message = ''
        return {'message': message}
