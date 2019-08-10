"""
Unitpages editing form.
"""
#######################################################################

from django import forms
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from markuphelpers.forms import LinedTextareaWidget, ReStructuredTextFormMixin

from .models import Asset, Page, SiteFile

#######################################################################


#######################################################################


class PageBaseForm(ReStructuredTextFormMixin, forms.ModelForm):
    """
    A form for the Django admin unitpages.
    """

    restructuredtext_fields = [("content", True)]

    class Meta:
        model = Page
        widgets = {
            "title": forms.TextInput(attrs={"size": 60}),
            "content": LinedTextareaWidget,
        }
        exclude = []

    # Similar to  django.contrib.flatpages.forms
    def clean_url(self):
        url = self.cleaned_data["url"]
        if not url.startswith("/"):
            raise forms.ValidationError(
                ugettext("URL is missing a leading slash."),
                code="missing_leading_slash",
            )

        if (
            settings.APPEND_SLASH
            and (
                (
                    settings.MIDDLEWARE
                    and "django.middleware.common.CommonMiddleware"
                    in settings.MIDDLEWARE
                )
                or "django.middleware.common.CommonMiddleware"
                in settings.MIDDLEWARE_CLASSES
            )
            and not url.endswith("/")
        ):
            raise forms.ValidationError(
                ugettext("URL is missing a trailing slash."),
                code="missing_trailing_slash",
            )

        same_url = Page.objects.filter(url=url)
        if self.instance.pk:
            same_url = same_url.exclude(pk=self.instance.pk)

        if same_url.exists():
            raise forms.ValidationError(
                _("Page with url %(url)s already exists"),
                code="duplicate_url",
                params={"url": url},
            )

        return url


#######################################################################


class AdminPageForm(PageBaseForm):
    """
    A form for the Django admin unitpages.
    """

    # As per django.contrib.flatpages.forms
    url = forms.RegexField(
        label=_("URL"),
        max_length=100,
        regex=r"^[-\w/\.~]+$",
        help_text=_(
            "Example: '/about/contact/'. Make sure to have leading and trailing slashes."
        ),
        error_messages={
            "invalid": _(
                "This value must contain only letters, numbers, dots, "
                "underscores, dashes, slashes or tildes."
            )
        },
        widget=forms.TextInput(attrs={"size": 60}),
    )

    class Meta(PageBaseForm.Meta):
        pass

    class Media:
        js = (staticfiles_storage.url("pages/js/clipboard.min.js"),)


#######################################################################


class PageForm(PageBaseForm):
    """
    A form for updating unitpages.
    """

    class Meta(PageBaseForm.Meta):
        exclude = ["url"]

    class Media:
        css = {
            "all": (
                staticfiles_storage.url("css/forms.css"),
                staticfiles_storage.url("css/twoColumn.css"),
            )
        }
        js = (
            staticfiles_storage.url("js/jquery.formset.js"),
            staticfiles_storage.url("pages/js/clipboard.min.js"),
        )


#######################################################################


def get_asset_formset_class(
    form=forms.ModelForm, formset=forms.BaseInlineFormSet, **kwargs
):
    return forms.inlineformset_factory(Page, Asset, form, formset, **kwargs)


#######################################################################
