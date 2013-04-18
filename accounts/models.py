from django.db import models
from django.contrib.auth.models import User

from userena.models import UserenaBaseProfile

def is_positive(value):
    """ Just checks to see that `value` is a positive number """
    return value >= 0
    
class UserProfile(UserenaBaseProfile):
    """    """    
    user = models.OneToOneField(User, unique=True)
    credit = models.IntegerField(default=0)

    def get_balance(self):
        """ Return the amount of SMS available to the user """
        return self.credit

    def add_credit(self, value):
        """
        Add [value] SMS to the user's account. Returns the new value of
        self.credit.
         """
        # If a negative figure ever gets supplied to the method, just
        # fail.
        if not is_positive(value):
            raise InvalidTransaction

        # I'm limiting the maximum number that can be added at once to
        # `MAXIMUM_VALUE`
        if not MAXIMUM_VALUE >= value:
            raise NumberTooBig
            
        # coerce `value` to int just in case a float is supplied
        value = int(value)
        self.credit = self.credit + value
        return self.credit 

    def deduct_credit(self, value):
        """
        Deduct [value] SMS from the user's account. Returns the new
        value of self.credit
        """
        # Ideally there should not be a situation where there would be
        # an attempt to deduct more than is available. The frontend
        # should take care of that but there should be checks here.

        # If a negative value ever gets supplied to the method, fail.
        if not is_positive(value):
            raise InvalidTransaction

        # coerce `value` to int just in case a float is supplied
        value = int(value)
        if self.credit < value:
            raise InvalidTransaction
        else:
            self.credit = self.credit - value
        return self.credit

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u, defaults={'credit':10})[0])
