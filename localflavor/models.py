from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import CharField

class MobilePhoneNumberField(CharField):
    """
    This Field will only accept Nigeria mobile phone numbers in the
    format:
    * 08008009000

    The following will not be accepted:
    * 23480080090000
    * 23418008009000
    * 8008009000

    Validated input will be returned in the format:
    * 0800-800-9000
    """
    
    description = _("Phone number")
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 14
        super(MobilePhoneNumberField, self).__init__(*args, **kwargs)
        
    def formfield(self, **kwargs):
        from messaging.localflavor.forms import NigerianMobileNumberField
        defaults = {'form_class': NigerianMobileNumberField}
        defaults.update(kwargs)
        return super(MobilePhoneNumberField, self).formfield(**defaults)
