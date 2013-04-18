from backends.api import send_bulk_sms
from messaging.models import Sms, List, Contact

ROUTE_SMS_STATUS = {
                    '1701': 'Success', '1702': 'Invalid URL',
                    '1703': 'Invalid value in username or password field',
                    '1704': 'Invalid type', '1705': 'Invalid message',
                    '1706': 'Invalid Destination',
                    '1707': 'Invalid sender', '1708': 'Invalid dlr value',
                    '1709': 'User validation failed',
                    '1710': 'Internal Error', '1025': 'Insufficient credit'
}

class SmsBlaster(object):
    """
    Does the work of piecing together information of the sms to be sent,
    forwarding it to the functions to do the low level sending and then
    and returns a list of tuples where each tuple contains a status code
    and the destination number for which the code relates.
    """
    def __init__(self, text, numbers=None, user_profile=None, sms_class=Sms, sent_by=None):
        self.text = text
        self.numbers = numbers
        self.user_profile = user_profile
        self.sms_class = sms_class
        self.sms_instance = None
        self.sent_by = sent_by
        self.contact_list = []
        self.successful = []
        self.failed = []
        self.send_list = []

    def is_ok(self, res):
        if res in ROUTE_SMS_STATUS:
            return ROUTE_SMS_STATUS[res] == ROUTE_SMS_STATUS['1701']

    def process(self):
        """
        passes sms information needed by the backend to send an sms.
        """
        if isinstance(self.numbers, basestring):
            to = [self.numbers]
        else:
            to = self.numbers
        response = send_bulk_sms(self.text, number_list=to, user_profile=self.user_profile, sent_by=self.sent_by) # [(0,2348058068419)]
        self.analyse(response)

    def analyse(self,response):
        """
        parses the response and stores the successful and unsuccessful
        sms.
        reponse is in this format [('1701','2348088080088')]
        """
        if response == 0:   # Please work on this. Its possibly redundant
            if isinstance(self.numbers, basestring):
                self.failed.append(unicode(self.numbers))
            elif isinstance(self.numbers, list):
                self.failed.extend(self.numbers)
                
        else:
            msg = self.create_or_get_sms_instance()
            
            for res in response:
                if self.is_ok(res[0]):
                    self.successful.append(unicode(res[1]))
                else:
                    self.failed.append(unicode(res[1]))
                    
                self.send_list.append(List(message=msg, number= res[1]))
                
    @property
    def information(self):
        info = {
                'text':self.text, 'successful':self.successful,
                'failed':self.failed, 'sms_instance':self.sms_instance
        }
        return info

    def create_or_get_sms_instance(self):
        if not self.sms_instance:
            self.sms_instance = self.sms_class.objects.create(sender=self.user_profile.user, body=self.text, sender_alias=self.sent_by)
        return self.sms_instance

    def create_contacts_and_list(self):
        if not self.send_list:
            return

        # make the List
        List.objects.bulk_create(self.send_list)

        # Now save contacts without duplicates...
        all_numbers = self.successful + self.failed
        
        # The below query should give us a list of numbers that are already
        # associated with contacts in the database
        prev_saved_contacts = Contact.objects.filter(number__in=all_numbers).values_list('number', flat=True)

        # weed un-needed numbers using sets
        all_nums_set = set(all_numbers)
        database_nums_set = set(prev_saved_contacts)

        to_save_set = all_nums_set.symmetric_difference(database_nums_set)
        to_save = list(to_save_set)
        to_save_list = [Contact(number=num) for num in to_save]
        

        Contact.objects.bulk_create(to_save_list)

    def adjust_credit(self):
        number = len(self.successful)
        self.user_profile.deduct_credit(number)
        self.user_profile.save()

    def blast(self):
        self.process()
        self.create_contacts_and_list()
        self.adjust_credit()
        return self.information
