from django.forms.widgets import Widget
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class ReadOnly(Widget):
    """Some of these values are read only - just a bit of text..."""
    def render(self, name, value, attrs=None):
        value = force_unicode(value)
        return mark_safe('%s' %value)
