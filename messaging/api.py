from tastypie.resources import ModelResource
from messaging.models import Sms

class SmsResource(ModelResource):
    class Meta:
        queryset = Sms.objects.all()
        resource_name = 'sms'
