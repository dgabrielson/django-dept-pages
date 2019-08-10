# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Page",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text=b"Uncheck this to remove this item without actually deleting it.",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                (
                    "public",
                    models.BooleanField(
                        default=True,
                        help_text=b"Check this to includes the page in the sitemap",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text=b"A url fragment that identifies this page.  Must be globablly unique for all pages",
                        unique=True,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text=b"A short, meaningful title", max_length=100
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        help_text=b'Page content. This will be processed as <a href="http://docutils.sourceforge.net/docs/user/rst/quickstart.html" target="_blank">ReStructuredText</a>',
                        blank=True,
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        blank=True,
                        to="unitpages.Page",
                        help_text=b"The parent page for this page, if it has one",
                        null=True,
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="SiteFile",
            fields=[
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text=b"Uncheck this to remove this item without actually deleting it.",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text=b"A url fragment that identifies this resource.  Must be globablly unique for all site files",
                        serialize=False,
                        primary_key=True,
                    ),
                ),
                ("file", models.FileField(upload_to=b"unitpages/%Y/%m")),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
    ]
