"""
Unitpages models
"""
############################################################################
###############
from __future__ import print_function, unicode_literals

import os

from django.conf import settings
from django.db import models
from django.urls import get_script_prefix
from django.utils.encoding import iri_to_uri, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import conf

###############


############################################################################


class UnitpageBaseModel(models.Model):
    """
    An abstract base class.
    """

    active = models.BooleanField(
        default=True,
        help_text=_(
            "Uncheck this to remove this item " + "without actually deleting it."
        ),
    )
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name=_("creation time")
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name=_("last modification time")
    )

    class Meta:
        abstract = True


############################################################################


@python_2_unicode_compatible
class SiteFile(UnitpageBaseModel):

    slug = models.SlugField(
        primary_key=True,
        unique=True,
        help_text=_(
            "An identifer for "
            + "this resource that will be used in urls.  Must be globablly "
            + "unique for all site files.  "
            + "Use lower case, dashes, and numbers only."
        ),
        verbose_name=_("URL fragment"),
    )
    file = models.FileField(
        upload_to=conf.get("upload_to"), storage=conf.get("storage")
    )

    def get_absolute_url(self):
        return self.file.url

    def __str__(self):
        return self.slug


############################################################################


@python_2_unicode_compatible
class Page(UnitpageBaseModel):

    public = models.BooleanField(
        default=True, help_text=_("Check this to includes the page in the sitemap")
    )

    url = models.CharField(_("URL"), max_length=100, db_index=True)
    title = models.CharField(max_length=100, help_text=_("A meaningful title"))
    short_title = models.CharField(
        max_length=32, blank=True, help_text=_("A much shorter alternate title")
    )
    content = models.TextField(blank=True, help_text=conf.get("page_content_help"))

    def __str__(self):
        return self.title

    def get_short_title_display(self):
        if self.short_title:
            return self.short_title
        return self.title

    def get_absolute_url(self):
        return iri_to_uri(get_script_prefix().rstrip("/") + self.url)

    def breadcrumbs(self):
        parts = self.url.split("/")
        if not parts[-1]:
            parts = parts[:-1]
        if not parts[0]:
            parts = parts[1:]
        url_list = []
        for i in range(1, len(parts)):
            url_part = "/" + "/".join(parts[:i])
            if settings.APPEND_SLASH:
                url_part += "/"
            url_list.append(url_part)
        title_list = []
        page_qs = Page.objects.filter(active=True, url__in=url_list).values_list(
            "url", "title", "short_title"
        )
        page_d = {url: (tl, ts) for url, tl, ts in page_qs}
        for url in url_list:
            title_list.append(page_d.get(url, None))
        return [
            (url, title[1] or title[0])
            for url, title in zip(url_list, title_list)
            if url is not None and title is not None
        ]


############################################################################


@python_2_unicode_compatible
class Asset(UnitpageBaseModel):
    """
    A file asset for a page.
    """

    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, limit_choices_to={"active": True}
    )
    file = models.FileField(
        upload_to=conf.get("upload_to"), storage=conf.get("storage")
    )
    description = models.CharField(max_length=250, blank=True)

    def get_absolute_url(self):
        return self.file.url

    get_absolute_url.short_description = "url"

    def __str__(self):
        name = os.path.basename(self.file.name)
        if self.description:
            name += ": " + self.description
        return name


############################################################################

#
