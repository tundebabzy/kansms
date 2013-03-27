from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def get_connection(path=None, fail_silently=False, **kwargs):
    """
    Load an sms backend and return an instance of it.
    """

    path = path or getattr(settings, 'SMSING_BACKEND',
                                'backends.osheap.SmsBackend')
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except AttributeError as e:
        raise ImproperlyConfigured(u'Error importing sms backend module %s: "%s"' % (mod_name, e))

    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" class' % (mod_name, klass_name))

    return klass(fail_silently=fail_silently, **kwargs)

def _connection(fail_silently=None, username=None, password=None,
                connection=None):
    connection = connection or get_connection(
        fail_silently = fail_silently,
        username = username,
        password = password,
    )
    return connection
    

def send_sms(text, to, fail_silently=False,
             username=None, password=None, connection=None):
    """
    This uses the backend to send a single SMS.
    
    This should be used for a single message. For bulk messages, use
    `send_bulk_sms`
    """
    from backends.messaging import Message
    if not to:
        # We are not going to send a message to nobody so just fail
        return 
    if isinstance(to, list):
        connection = _connection(fail_silently, username, password, connection)
        message = Message(text=text, to=to)
        return connection.send_messages(message)

def send_bulk_sms(text, number_list, fail_silently=False,
             username=None, password=None, connection=None):
    """
    This uses the backend to send multiple messages.
    
    `datatuple` should be in the form: (text, to)
    eg datatuple::('What time is it? Call me', '0810').

    This should be used for bulk messages. For just a single message,
    use `send_sms`.
    """
    from backends.messaging import Message
    connection = _connection(fail_silently, username, password, connection)
    
    # Check datatuple for messages supplied with acceptable destination
    # numbers are queue *only* those for sending
    messages = []
    for m in number_list:
        messages.append(Message(text=text, to=m))
    return connection.send_messages(messages)
