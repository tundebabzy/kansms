"""
Nigeria specific Form helpers
"""

from __future__ import absolute_import

import re

from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError
from django.forms.fields import CharField
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode

COUNTRY_PREFIX = ['234']

OPERATOR_PREFIX = ['802', '803', '805', '806', '807', '808',
    '809', '810', '813', '815', '816', '819', '703', '705',
    '706', '814', '811', '708']
    
mobile_number_re = re.compile(
        """
        ^
        (\d{3})*    #   Match the country code for Nigeria
        (0)*          #   
        (\d{3})     #   Match the OPERATOR_PREFIX
        (\d{3})     #   Next 3 digits
        (\d{4})     #   Match last 4 digits
        $
        """
        , re.VERBOSE)

def _get_cleaned_number(n):
    s = list(n.groups())

    # If '234' is missing, lets add it...
    s[0] = s[0] or '234'

    # if group 2 is present, remove it anyway...
    s.pop(1)

    # finally convert the list to string...
    return ''.join(s)


class NigerianMobileNumberField(CharField):
    default_error_messages = {
        'invalid': 'Check that you supplied only one phone number and that the \
        format is valid'
        }
        
    def clean(self, value):
        super(NigerianMobileNumberField, self).clean(value)
        
        if value in EMPTY_VALUES:
            return u''
            
        value = re.sub('(\s+)', '', smart_unicode(value))
        not_allowed = re.compile(r'\D')
        x = not_allowed.search(value)
        if x:
            raise ValidationError(self.error_messages['invalid'])
            
        number = mobile_number_re.search(value)
        if number:
            if number.group(1) in COUNTRY_PREFIX or number.group(1) == None:
                if number.group(3) in OPERATOR_PREFIX:
                    cleaned_number = _get_cleaned_number(number)
                    return cleaned_number
                else:
                    raise ValidationError("""The number you supplied does
            not seem to be a valid Nigerian cell phone numbers. Please
            check and confirm.""")

        raise ValidationError(self.error_messages['invalid'])
        
class MultipleNaijaMobileNumberField(CharField):        
    default_error_messages = {
        'invalid': 'Phone numbers must be in this format. eg: \
                    08058009999 and make sure that the numbers are \
                    separated by commas (,) a new line or a space eg 08058009999, \
                    08038009999 08098009999'
        }

    def clean(self, value):
        super(MultipleNaijaMobileNumberField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        value = re.sub('(\s+)', ' ', smart_unicode(value))
        
        # This is the regexp that should catch the characters we don't
        # want to work with. I don't want to try and correct things too
        # much in case the corrections could by some luck cause some
        # incorrect numbers to be pushed to the backend for sending
        # hence once any unexpected character is found, bail.
        not_allowed = re.compile(r'\D ')
        x = not_allowed.search(value)
        
        if x:
            raise ValidationError(self.error_messages['invalid'])
        
        value = value.replace(',',' ').split()
        errors, operator_error, final_numbers = [], [], []

        # I'm going to loop through every number that has made it through
        # to this point and reject all the ones that fail validation.
        # Considering the fact that the user could potentially have
        # supplied hundreds of malformed or unacceptable phone numbers,
        # the user will be happier to see all the offending numbers
        # at once.        
        for n in value:
            number = mobile_number_re.search(n)
            if not number:
                errors.append(n)
            else:
                if number.group(1) in COUNTRY_PREFIX or number.group(1) == None:
                    if number.group(3) not in OPERATOR_PREFIX:
                        operator_error.append(n)
                    else:
                        cleaned_number = _get_cleaned_number(number)
                        final_numbers.append(cleaned_number)
                else:
                    errors.append(n)
                        
        if errors:
            raise ValidationError(
            'Please check and make sure that the following numbers you \
            supplied are in the correct format i.e XXXYYYZZZZ \
            e.g 08050009999.: %s' % ','.join([u' %s' % e for e in errors]))
        if operator_error:
            raise ValidationError(
            'The following number(s) you supplied does not seem to be \
            valid Nigerian cell phone numbers. Please check and confirm \
            them : %s' % ','.join([u' %s' %e for e in operator_error]))
        return final_numbers
