"""
Admin interface for unitpages.
"""
#######################################################################

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .forms import AdminPageForm
from .models import Asset, Page, SiteFile

#######################################################################

MyModelAdmin = None
use_guardian = False
if getattr(settings, "GUARDED_MODEL_ADMIN_ENABLED", True):
    # automatically use guardian, if installed
    try:
        from guardian.admin import GuardedModelAdmin
    except ImportError:
        pass
    else:
        MyModelAdmin = GuardedModelAdmin
        use_guardian = True
if MyModelAdmin is None:
    MyModelAdmin = admin.ModelAdmin


if use_guardian:
    from guardian.shortcuts import get_objects_for_user

#######################################################################

if use_guardian:

    class RestrictedModelAdmin(GuardedModelAdmin):
        """
        NOTE: Access can be restricted to only the users guardian objects.

        NOT PERFECT, because a limited guardian user can further
        delegate to other users; however those other users ALSO
        required is_staff and the 'change_<object>' global permission.
        """

        def has_change_permission_for_all(self, request):
            return super(RestrictedModelAdmin, self).has_change_permission(request)

        def _is_restricted_admin(self, request):
            permname = self._get_permname("change")
            change_all = self.has_change_permission_for_all(request)
            if change_all:
                return False
            change_some = get_objects_for_user(request.user, permname).exists()
            if change_some:
                return True
            return False

        def _get_permname(self, permtype):
            """
            permtype is one of: 'add', 'change', 'delete'
            """
            opts = self.opts
            codename = get_permission_codename("change", opts)
            permname = "%s.%s" % (opts.app_label, codename)
            return permname

        def get_queryset(self, request):
            """
            Return a custom queryset based on access.
            """
            qs = super(RestrictedModelAdmin, self).get_queryset(request)

            if request.user.is_superuser:
                return qs
            if self._is_restricted_admin(request):
                permname = self._get_permname("change")
                # TODO: maybe filter original queryset based on this one?
                qs = get_objects_for_user(request.user, permname)
            return qs

        def has_change_permission(self, request, obj=None):
            if (obj is None) and self._is_restricted_admin(request):
                return True
            permname = self._get_permname("change")
            if self._is_restricted_admin(request):
                flag = request.user.has_perm(permname, obj)
            else:
                flag = self.has_change_permission_for_all(request)
            return flag

        def has_module_permission(self, request):
            result = super(RestrictedModelAdmin, self).has_module_permission(request)
            if result:
                return True
            if not request.user.is_staff:
                return False
            permname = self._get_permname("change")
            if get_objects_for_user(request.user, permname).exists():
                return True
            return False

        def get_readonly_fields(self, request, obj=None):
            result = super(RestrictedModelAdmin, self).get_readonly_fields(request, obj)
            if hasattr(
                self, "restricted_readonly_fields"
            ) and self._is_restricted_admin(request):
                result = tuple(result) + tuple(self.restricted_readonly_fields)
            return result

    MyModelAdmin = RestrictedModelAdmin

#######################################################################


#######################################################################


class SiteFileAdmin(MyModelAdmin):
    list_display = ["slug", "file"]
    ordering = ["slug"]
    search_fields = ["slug", "file"]
    restricted_readonly_fields = ["slug"]


admin.site.register(SiteFile, SiteFileAdmin)


#######################################################################


class AssetInline(admin.TabularInline):
    model = Asset
    fields = ["file", "description", ("current_url", "changelist_buttons")]
    readonly_fields = ["current_url", "changelist_buttons"]
    extra = 0

    def current_url(self, obj):
        if obj.pk:
            return format_html(
                '<span id="copy-target-{}">{}</span>'.format(
                    obj.pk, obj.get_absolute_url()
                )
            )
        return ""

    current_url.allow_tags = True

    def changelist_buttons(self, obj):
        """
        At the moment this is not used becuase we need to determine
        the selector #{{ form.prefix }} td.field-get_absolute_url p
        """
        if obj.pk:
            return format_html(
                '<button type="button" class="copy-btn" data-clipboard-target="#copy-target-{}">Copy url</button>'.format(
                    obj.pk
                )
            )
        return ""

    changelist_buttons.short_description = "Actions"
    changelist_buttons.allow_tags = True


###############################################################


class PageAdmin(MyModelAdmin):
    inlines = [AssetInline]
    list_display = ["url", "title", "active", "public"]
    list_filter = ["active", "public", "created", "modified"]
    search_fields = ["title", "short_title", "content"]
    ordering = ["url", "title"]
    form = AdminPageForm
    restricted_readonly_fields = ["url"]
    # required to override django-guardian template override:
    change_form_template = "admin/unitpages/page/change_form.html"


admin.site.register(Page, PageAdmin)


#######################################################################
