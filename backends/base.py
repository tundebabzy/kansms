from django.core.exceptions import ImproperlyConfigured

class BaseBackend(object):
    """
    Base class for backend implementations.

    This should be overridden to create backend implementations.
    """
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently

    def open(self):
        """
        Opens a connection to a backend
        """
        pass

    def get_username(self):
        """
        Returns username for backend authentication where applicable
        """
        pass

    def get_password(self):
        """
        Returns username for backend authentication where applicable
        """
        pass

    def send_messages(self, messages):
        """
        Sends one or more Message objects and should return the number
        sent. This should be used for multiple messages. Custom
        backends must at least over write this method.
        """
        pass
