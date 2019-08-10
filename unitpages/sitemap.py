"""
Sitemap for unitpages application
"""

from django.contrib.sitemaps import Sitemap

from .models import Page


class Page_Sitemap(Sitemap):
    """
    Sitemap for Page objects
    """

    #    priority = 0.5
    #    changefreq = 'monthly'

    def items(self):
        """
        Return the items for this map
        """
        return Page.objects.filter(active=True, public=True)

    def lastmod(self, item):
        """
        Last Modification datetime.
        """
        return item.modified
