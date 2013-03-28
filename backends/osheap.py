"""
O'sheap backend.
"""

from base import BaseBackend
from messaging import Message
from django.conf import settings
from kannel.kannel import InfobipSmsSender as SmsSender

USERNAME = getattr(settings, 'SMS_GATEWAY_USERNAME', '')
#USERNAME = 'citrusSMS'
#USERNAME = 'citrus'
PASSWORD = getattr(settings, 'SMS_GATEWAY_PASSWORD', '')
#PASSWORD = 'citrus789'
#PASSWORD = 'smsdep13'
PORT = getattr(settings, 'SMS_GATEWAY_PORT', '')
SERVER = getattr(settings, 'SMS_GATEWAY_API_URL', '')
#ROUTE_SERVER = 'smsplus2.routesms.com'
#INFOBIP_URL = 'api.infobip.com/api/v3/sendsms/plain'

class SmsBackend(BaseBackend):
    sms_sender = SmsSender(username=USERNAME, password=PASSWORD, server=SERVER, port=PORT)
    def send_messages(self, messages, sender=None):
        if not messages:
            return 0
        valid_messages = check_args(messages)
        msg = self.sms_sender.send(
            message_instance_list = valid_messages,
            sent_by = sender
        )
        return msg
                        
def check_args(messages):
    """
    expected args should be a list of Message objects.
    """
    assert isinstance(messages, list), """Supply a list of Message objects."""
    valid_messages = []
    for message in messages:
        if isinstance(message, Message):
            valid_messages.append(message)
    return valid_messages
