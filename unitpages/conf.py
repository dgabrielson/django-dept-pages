"""
The DEFAULT configuration is loaded when the named _CONFIG dictionary
is not present in your settings.
"""

CONFIG_NAME = "UNITPAGES_CONFIG"  # must be uppercase!


from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.translation import ugettext_lazy as _

DEFAULT = {
    # 'storage' is the storage backend for files.
    # (optional)
    "storage": default_storage,
    # 'upload_to' is the variable portion of the path where files are stored.
    # (optional)
    "upload_to": "pages/%Y/%m",
    "page_content_help": _(
        "Page content. "
        + "This will be processed as "
        + '<a href="http://docutils.sourceforge.net/docs/user/rst/quickstart.html"'
        + ' target="_blank">ReStructuredText</a>'
    ),
}


def get(setting):
    """
    get(setting) -> value

    setting should be a string representing the application settings to
    retrieve.
    """
    assert setting in DEFAULT, "the setting %r has no default value" % setting
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return app_settings.get(setting, DEFAULT[setting])


def get_all():
    """
    Return all current settings as a dictionary.
    """
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return dict(
        [(setting, app_settings.get(setting, DEFAULT[setting])) for setting in DEFAULT]
    )
