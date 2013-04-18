from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.forms import ModelForm
from messaging.exceptions import InvalidTransaction, NumberTooBig
from string import capwords

MAXIMUM_VALUE = 1000000
    
class List(models.Model):
    message = models.ForeignKey('Sms', related_name='sms_id')
    number = models.CharField(max_length=15)
    
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
    sender_alias = models.CharField(max_length=14, blank=False, null=True)
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

#def add_to_group(sender, instance, created, **kwargs):
#    from django.contrib.auth.models import Group
#
#    if created:
#        try:
#            group = Group.objects.get(name='Normal Users')
#            instance.groups.add(group)
#        except:
#            pass 
#post_save.connect(add_to_group, sender=User)
