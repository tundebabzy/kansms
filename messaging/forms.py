from django import forms
from django.forms.util import ErrorList
from django.utils.safestring import mark_safe
from localflavor.forms import NigerianMobileNumberField, MultipleNaijaMobileNumberField

from messaging.models import Group, Contact 

DELIVERY_METHOD = (
                    ('SR', 'Single Reciepient'),
                    ('BR', 'Bulk Reciepients'),
                    ('FU', 'File upload (For numbers contained in a .txt or .csv file)')
                )
                
class MessageForm(forms.Form):
    sender = forms.CharField(max_length=14)
    message = forms.CharField(widget=forms.Textarea, required=False)
    method = forms.ChoiceField(choices=DELIVERY_METHOD, label="Method for Supplying Receipients' Number(s)")
    save_message = forms.BooleanField(required=False)

class SingleReceipientForm(forms.Form):
    single_receipient = NigerianMobileNumberField(
        help_text='Enter a single number')

class BulkReceipientForm(forms.Form):
    bulk_receipient = MultipleNaijaMobileNumberField(widget=forms.Textarea,
        label='Bulk Receipients', help_text='Seperate numbers with a comma (,)\
        or a new line(pressing the Enter key)')

class FileUploadForm(forms.Form):
    file_name = forms.FileField(label='Upload file containing your numbers. Must be in .CSV or .txt format',
                                help_text='maximum size = 1MB')

class MessageFormError(ErrorList):
    def __unicode__(self):
        return self.error_html()

    def error_html(self):
        if not self:
            return u''
        return mark_safe(u'<div class="error">%s</div>' % ''.join([u'<small>%s</small>' % e for e in self]))
