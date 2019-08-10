"""
Haystack search indexes for UnitPages application.
"""
###############################################################

from haystack import indexes

from .models import Page, SiteFile

###############################################################


class PageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    pub_date = indexes.DateTimeField(model_attr="modified")
    title = indexes.CharField(model_attr="title", boost=4.0)

    def get_model(self):
        return Page

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(active=True, public=True)

    def prepare(self, obj):
        """
        Do document boosting.
        """
        data = super(PageIndex, self).prepare(obj)
        data["boost"] = 3.0
        return data


###############################################################
