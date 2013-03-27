from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.forms import ModelForm
from messaging.exceptions import InvalidTransaction, NumberTooBig
from string import capwords

MAXIMUM_VALUE = 1000000

def is_positive(value):
    """ Just checks to see that `value` is a positive number """
    return value >= 0
    
class List(models.Model):
    message = models.ForeignKey('Sms', related_name='sms_id')
    #contact = models.ForeignKey('Contact')
    number = models.CharField(max_length=15)
    #first_name = models.CharField(max_length=30, blank=True, null=True)
    #last_name = models.CharField(max_length=30, blank=True, null=True)
    #email = models.EmailField(blank=True, null=True)
    #saved = models.BooleanField(default=False)
    
    def __unicode__(self):
        return '%s' %self.number

class Contact(models.Model):
    #owner = models.ForeignKey(User)
    first_name = models.CharField(max_length=30, blank=False, null=True)
    last_name = models.CharField(max_length=50, blank=False, null=True)
    number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)

    def __unicode__(self):
        return '%s %s' %(self.first_name, self.last_name)

class Group(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return '%s' %self.name

class ContactGroup(models.Model):
    owner = models.ForeignKey(User)
    contact = models.ForeignKey(Contact)
    group = models.ForeignKey(Group)

    def __unicode__(self):
        return '%s' %self.group

class Sms(models.Model):
    # model name changed from Draft to Sms
    sender = models.ForeignKey(User, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    trash = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s' % self.body

    @models.permalink
    def get_absolute_url(self):
        return('send_to_others', (), {'msg_id': self.pk,})

    def is_draft(self):
        return to_save
        
class UserProfile(models.Model):
    """
    Extend django.auth.User to add an extra field: credit
    """    
    user = models.OneToOneField(User)
    credit = models.IntegerField(default=0)

#    def save(self, *args, **kwargs):
#        # Although there will be checks in other places, lets still
#        # make sure a negative figure never gets saved
#        if not is_positive(self.credit):
#            return
#        return super(UserProfile, self).save(*args, **kwargs)

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

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u, defaults={'credit':0})[0])

def add_to_group(sender, instance, created, **kwargs):
    from django.contrib.auth.models import Group

    if created:
        try:
            group = Group.objects.get(name='Normal Users')
            instance.groups.add(group)
        except:
            pass 
post_save.connect(add_to_group, sender=User)
