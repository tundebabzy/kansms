from accounts import forms
from userena import views as userena_views
from django.http import Http404

def profile_edit(request, username, edit_profile_form=forms.KansmsEditProfileForm,
                 template_name='userena/profile_form.html', success_url=None,
                 extra_context=None, **kwargs):
    
    return userena_views.profile_edit(request=request, username=username,
            edit_profile_form=edit_profile_form, template_name=template_name,
            success_url=success_url, extra_context=extra_context)

def not_allowed(request):
    raise Http404
