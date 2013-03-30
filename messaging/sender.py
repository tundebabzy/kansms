from backends.api import send_bulk_sms
from messaging.models import Sms, List, Contact

class SmsBlaster(object):
    """
    Does the work of piecing together information of the sms to be sent,
    forwarding it to the functions to do the low level sending and then
    and returns a list of tuples where each tuple contains a status code
    and the destination number for which the code relates.
    """
    def __init__(self, text, numbers=None, user=None, sms_class=Sms, sent_by=None):
        self.text = text
        self.numbers = numbers
        self.user = user
        self.sms_class = sms_class
        self.sms_instance = None
        self.sent_by = sent_by
        self.contact_list = []
        self.successful = []
        self.failed = []
        self.send_list = []

    def process(self):
        """
        passes sms information needed by the backend to send an sms.
        """
        if isinstance(self.numbers, basestring):
            to = [self.numbers]
        else:
            to = self.numbers
        response = send_bulk_sms(self.text, number_list=to, user=self.user, sent_by=self.sent_by) # [(0,2348058068419)]
        self.analyse(response)

    def analyse(self,response):
        """
        parses the response and stores the successful and unsuccessful
        sms
        """
        msg = self.create_or_get_sms_instance()
        
        for res in response:
            if res[0] == '0' or res[0] == 0 or res[0] == '1701' or res[0] == 1701:
                self.successful.append(str(res[1]))
            else:
                self.failed.append(str(res[1]))
                
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
            self.sms_instance = self.sms_class.objects.create(sender=self.user, body=self.text, sender_alias=self.sent_by)
        return self.sms_instance

    def create_contacts_and_list(self):
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

    def blast(self):
        self.process()
        self.create_contacts_and_list()
        return self.information
