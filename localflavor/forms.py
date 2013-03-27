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

OPERATOR_PREFIX = ['0802', '0803', '0805', '0806', '0807', '0808',
    '0809', '0810', '0813', '0815', '0816', '0819', '0703', '0705',
    '0706']
    
mobile_number_re = re.compile(
        """
        ^
        (\d{4})     #   Match the OPERATOR_PREFIX
        (\d{3})     #   Next 3 digits
        (\d{4})     #   Match last 4 digits
        $
        """
        , re.VERBOSE)

class NigerianMobileNumberField(CharField):
    default_error_messages = {
        'invalid': 'Check that you supplied a single phone number and that the \
        phone number is in this format eg: 2348058009999'
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
            if number.group(1) in OPERATOR_PREFIX:
                return u'234%s%s%s' %(number.group(1)[1:], number.group(2), 
                                            number.group(3))
            else:
                raise ValidationError(self.error_messages['invalid'])
        raise ValidationError(self.error_messages['invalid'])
        
class MultipleNaijaMobileNumberField(CharField):        
    default_error_messages = {
        'invalid': 'Phone numbers must be in this format. eg: \
                    2348058009999. Also make sure that the numbers are \
                    separated by commas (,) a new line or a space eg 2348058009999, \
                    2348038009999 2348098009999'
        }

    def clean(self, value):
        super(MultipleNaijaMobileNumberField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        value = re.sub('(\s+)', '', smart_unicode(value))
        
        # This is the regexp that should catch the characters we don't
        # want to work with. I don't want to try and correct things too
        # much in case the corrections could by some luck cause some
        # incorrect numbers to be pushed to the backend for sending
        # hence once any unexpected character is found, bail.
        not_allowed = re.compile(r'[^0-9, ]')
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
            elif not errors:
                if number.group(1) not in OPERATOR_PREFIX:
                    operator_error.append(n)
                t = u'234%s%s%s' %(number.group(1)[1:], number.group(2),
                                    number.group(3))
                final_numbers.append(t)
        if errors:
            raise ValidationError(
            'Please check and make sure that the following numbers you \
            supplied are in the correct format i.e 234XXXYYYZZZZ \
            e.g 2348050009999.: %s' % ','.join([u' %s' % e for e in errors]))
        if operator_error:
            raise ValidationError(
            'The following number(s) you supplied does not seem to be \
            valid Nigerian cell phone numbers. Please check and confirm \
            them : %s' % ','.join([u' %s' %e for e in operator_error]))
        return final_numbers
        
