from string import capwords

from django.views.generic import ListView
from django.views.generic.edit import DeletionMixin
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from messaging.models import Sms

class SavedDraftListView(ListView, DeletionMixin):
    """
    This ListView subclass has deletion capabilities.
    """
    model = Sms
    template_name = 'saved.html'
    paginate_by = 10

    def can_delete_object(self, request):
        """
        Checks if the request has permission to delete a Sms object.
        """
        opts = self.model._meta
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission())

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SavedDraftListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SavedDraftListView, self).get_context_data(**kwargs)
        user = self.request.user
        user_balance = user.profile.get_balance()
        context.update({'credits': user_balance})
        return context

    def get_queryset(self):
        """
        Filters the original queryset by the logged in user and orders
        by its `created` field in descending order
        """
        queryset = super(SavedDraftListView, self).get_queryset()
        return queryset.filter(sender=self.request.user).order_by('-created')

    def paginate_queryset(self, queryset, page_size):
        """
        Very similar to the base paginate_queryset. The difference is
        that when it catches an InvalidPage Error, instead of raising a
        404, it changes `page_number` to the last page.
        """
        paginator = self.get_paginator(queryset, page_size,
                        allow_empty_first_page=self.get_allow_empty())
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(u'Page error')

        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage:
            page = paginator.page(paginator.num_pages)
            return (paginator, page, page.object_list, page.has_other_pages())

    def delete(self, request, *args, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        if self.can_delete_object(request):
            self.objects = self.get_delete_objects(request)
            self.objects.delete()

        # If the user has no delete permission, the system does not
        # complain. This would be very frustrating.
        #TODO: message the user if he has no delete permission.
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        path = self.request.path #TODO: this can bring undesirable behavior
        context = self.get_context_data(object_list=self.object_list)
        url_page_var = context['page_obj'].number

        if int(url_page_var) != int(page):
            # paginator will run again :(
            return HttpResponseRedirect(self.get_redirect_url(path, url_page_var))
        return self.render_to_response(context)

    def get_delete_objects(self, request):
        # I would love to do some checks to make sure that the pks in
        # selected are verified to be among those presented to the user
        # in the page he was served.
        selected = request.POST.getlist(u'selected', None)
        queryset = self.get_queryset()
        return queryset.filter(pk__in=selected)

    def get_redirect_url(self, path, url_page_var):
        return '%s?page=%s' %(path, url_page_var)
