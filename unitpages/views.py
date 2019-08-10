"""
Views for unitpages
"""
#######################
from __future__ import print_function, unicode_literals

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (
    Http404,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import UpdateView

from .forms import PageForm, get_asset_formset_class
from .models import Page, SiteFile

#######################
#######################################################################


#######################################################################

# As per django.contrib.flatpages.views.flatpage
def get_page(url, queryset=None):
    """
    Get a page object by url.
    This does some fancy handling for ``APPEND_SLASH = True``;
    so the object returned *may* also be None, which indicates
    that a page with a trailing slash was found.
    """
    if queryset is None:
        queryset = Page.objects.filter(active=True)

    if not url.startswith("/"):
        url = "/" + url
    try:
        page = get_object_or_404(queryset, url=url)
    except Http404:
        if not url.endswith("/") and settings.APPEND_SLASH:
            url += "/"
            page = get_object_or_404(queryset, url=url)
            return None
        else:
            raise
    return page


#######################################################################


def unitpage(request, url, extra_data=None, template_name=None):
    """
    Find the page, serve it.
    """
    page = get_page(url)
    if page is None:
        return HttpResponsePermanentRedirect("%s/" % request.path)

    context = {"page": page}
    if extra_data is not None:
        context.update(extra_data)

    templates = [
        url.strip("/") + ".html",
        "pages/" + url.strip("/") + ".html",
        "unitpages/" + url.strip("/") + ".html",
        "unitpages/index.html",
    ]
    if template_name is not None:
        templates.insert(0, template_name)
    return render(request, templates, context)


#######################################################################


class SiteFileDetailView(BaseDetailView):
    """
    Provide a unified way of retrieving sitefiles.
    """

    queryset = SiteFile.objects.filter(active=True)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponseRedirect(self.object.file.url)


#######################################################################


class PageUpdateView(UpdateView):
    """
    Class for updating a page
    """

    form_class = PageForm
    queryset = Page.objects.all()
    formset_initial = {}
    formset_prefix = None
    slug_field = "url"

    def get_object(self, queryset=None):
        page = get_page(self.kwargs["url"], queryset)
        if page is None:
            raise Http404
        return page

    def get_formset_class(self):
        kwargs = {"fields": ("file", "description"), "extra": 1}
        return get_asset_formset_class(**kwargs)

    def get_formset_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.formset_initial.copy()

    def get_formset_prefix(self):
        """
        Returns the prefix to use for forms on this view
        """
        return self.formset_prefix

    def get_formset_kwargs(self):
        kwargs = {
            "initial": self.get_formset_initial(),
            "prefix": self.get_formset_prefix(),
            "instance": self.object,
        }

        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST, "files": self.request.FILES})
        return kwargs

    def get_formset(self, formset_class=None):
        """
        Returns an instance of the form to be used in this view.
        """
        if formset_class is None:
            formset_class = self.get_formset_class()
        return formset_class(**self.get_formset_kwargs())

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        context = super(PageUpdateView, self).get_context_data(**kwargs)
        if "formset" not in context:
            context["formset"] = self.get_formset()
        return context

    def form_valid(self, form, formset):
        """
        If the form is valid, save the associated model.
        """
        if not self.request.user.has_perm("unitpages.change_page", self.object):
            response = render(
                "403.html",
                {"test_file_msg": "You do not have permission to edit this page"},
            )
            response.status_code = 403
            return response

        result = super(PageUpdateView, self).form_valid(form)
        formset.save()
        return result

    def form_invalid(self, form, formset):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.object = self.get_object()
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)


#######################################################################

try:
    from guardian.decorators import permission_required
except ImportError:
    page_update = login_required(PageUpdateView.as_view())
else:
    page_update = permission_required("unitpages.change_page", (Page, "url", "url"))(
        PageUpdateView.as_view()
    )


#######################################################################
