"""
UnitPage url patterns.

NOTE: When including this file, if the application root url
is *not* the top level url, then the included path must
end with "/", otherwise the url handling breaks.

E.g.,

    url(r'^new-pages/', include('unitpages.urls')),
    url(r'^', include('unitpages.urls')),   # must be last!

"""

from django.conf.urls import url

from .views import SiteFileDetailView, page_update, unitpage

urlpatterns = [
    # root index page
    url(r"^$", unitpage, kwargs={"url": "/"}, name="unitpages-root"),
    # page editor
    url(r"^_update(?P<url>.*)$", page_update, name="unitpages-update"),
    # sitefile redirects
    url(
        r"^_files/(?P<slug>[\w-]+)/$",
        SiteFileDetailView.as_view(),
        name="unitpages-sitefile",
    ),
    url(
        r"^_files/(?P<slug>[\w-]+)$",
        SiteFileDetailView.as_view(),
        name="unitpages-sitefile-noslash",
    ),
    # catch everything else... but only if it ends with /
    url(r"^(?P<url>.*/)$", unitpage, name="unitpages-link"),
]
