"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from messaging.models import Folder
from django.contrib.auth.models import User
from messaging.models import UserProfile
from messaging.exceptions import InvalidTransaction, NumberTooBig


class IncomingBasic(TestCase):

    def setUp(self):
        self.inbox = Folder.objects.create(name='inbox')
        self.outbox = Folder.objects.create(name='OUTBOX')
        self.draft = Folder.objects.create(name='Draft')
        self.user = User.objects.create(username='stig')
        self.sule = User.objects.create(username='sule')
        
    def test_folder_name(self):
        self.assertEqual(self.inbox.name, 'Inbox')
        a = Folder.objects.create(name='INBOX')
        self.assertEqual(a.name, 'Inbox')
        b = Folder.objects.create(name='inBOX')
        self.assertEqual(b.name, 'Inbox')
        self.assertEqual(self.outbox.name, 'Outbox')
        self.assertEqual(self.draft.name, 'Draft')
        some_other = Folder.objects.create(name='some OTHER Folder')
        self.assertEqual(some_other.name, 'Some Other Folder')
        er = Folder.objects.create(name='')
        self.assertEqual(er.name, '')

    def test_userprofile_setup(self):
        # Initialise User and UserProfile
        profile = self.user.profile
        credit = profile.credit
        self.assertEqual(credit, 0)
        self.assertEqual(credit, profile.get_balance())
        profile.add_credit(10)
        self.assertEqual(profile.credit, 10)
        self.assertRaises(InvalidTransaction, profile.add_credit, -10)
        self.assertRaises(NumberTooBig, profile.add_credit, 1000001)
        self.assertEqual(profile.credit+1000000, profile.add_credit(1000000))
        self.assertRaises(InvalidTransaction, profile.deduct_credit, 100000000)
        self.assertEqual(profile.credit-500, profile.deduct_credit(500))
        self.assertRaises(InvalidTransaction, profile.deduct_credit, 523658845454658545)
        self.assertEqual(profile.credit, 0+10+1000000-500)

    def test_incoming_setup(self):
        # Incoming objects
        from messaging.models import Incoming
        in1 = Incoming.objects.create(user=self.user, folder=self.inbox,
                    sender='+23418058009999', message='I LOVE YOU',
                    message_center='+23418058000000')
        in2 = Incoming.objects.create(user=self.user, folder=self.inbox,
                    sender='+23418058009991', message='Please call me.',
                    message_center='+23418058000000')
        in3 = Incoming.objects.create(user=self.sule, folder=self.inbox,
                    sender='+23418058009992', message='Sule baba!',
                    message_center='+23418058000000')
        user_msgs = Incoming.objects.filter(user=self.user, folder__name='Inbox')
        print '\n', user_msgs
        sule_msgs = Incoming.objects.filter(user=self.sule, folder__name='Inbox')
        print '\n', sule_msgs
        in3.send_to_trash()
        sule_msgs = Incoming.objects.filter(user=self.sule, folder__name='Inbox')
        print '\n', sule_msgs
        trash_msgs = Incoming.objects.filter(is_trash=True)
        print trash_msgs
        in2.move_to('New messages')
        user_msgs = Incoming.objects.filter(user=self.user, folder__name='Inbox')
        print user_msgs

