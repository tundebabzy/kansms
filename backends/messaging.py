from backends.api import get_connection

class Message(object):
    """ An SMS message """
    def __init__(self, to=None, text='', connection=None, **kwargs):
        """
        to:: type string
        text:: type string
        kannel has been configured for long messages.
        """
        self.to = to
        if text:
            assert isinstance(text, basestring), 'SMS text should be be \
            a string.'
        self.text = text
        self.connection = connection

    def get_text(self):
        if self.text:
            return self.text
        else:
            return '*Empty*'

    def set_text(self, value):
        self.text = value

    def del_text(self):
        del self.text

    message = property(get_text, set_text, del_text)
            

    def get_to(self):
        if self.to:
            return self.to
        else:
            return 'No number supplied.'

    def set_to(self, value):
        self.to = value

    def del_to(self):
        del self.to

    destination = property(get_to, set_to, del_to)
