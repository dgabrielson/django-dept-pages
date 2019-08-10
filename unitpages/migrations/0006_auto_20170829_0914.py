# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-29 14:14
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("unitpages", "0005_auto_20170602_1056")]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="active",
            field=models.BooleanField(
                default=True,
                help_text="Uncheck this to remove this item without actually deleting it.",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creation time"),
        ),
        migrations.AlterField(
            model_name="asset",
            name="file",
            field=models.FileField(upload_to="pages/%Y/%m"),
        ),
        migrations.AlterField(
            model_name="asset",
            name="modified",
            field=models.DateTimeField(
                auto_now=True, verbose_name="last modification time"
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="active",
            field=models.BooleanField(
                default=True,
                help_text="Uncheck this to remove this item without actually deleting it.",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="content",
            field=models.TextField(
                blank=True,
                help_text='Page content. This will be processed as <a href="http://docutils.sourceforge.net/docs/user/rst/quickstart.html" target="_blank">ReStructuredText</a>',
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creation time"),
        ),
        migrations.AlterField(
            model_name="page",
            name="modified",
            field=models.DateTimeField(
                auto_now=True, verbose_name="last modification time"
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                help_text="The parent page for this page, if it has one",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="unitpages.Page",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="public",
            field=models.BooleanField(
                default=True, help_text="Check this to includes the page in the sitemap"
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="slug",
            field=models.SlugField(
                help_text="A url fragment that identifies this page.  Must be globablly unique for all pages",
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="title",
            field=models.CharField(
                help_text="A short, meaningful title", max_length=100
            ),
        ),
        migrations.AlterField(
            model_name="sitefile",
            name="active",
            field=models.BooleanField(
                default=True,
                help_text="Uncheck this to remove this item without actually deleting it.",
            ),
        ),
        migrations.AlterField(
            model_name="sitefile",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creation time"),
        ),
        migrations.AlterField(
            model_name="sitefile",
            name="file",
            field=models.FileField(upload_to="pages/%Y/%m"),
        ),
        migrations.AlterField(
            model_name="sitefile",
            name="modified",
            field=models.DateTimeField(
                auto_now=True, verbose_name="last modification time"
            ),
        ),
        migrations.AlterField(
            model_name="sitefile",
            name="slug",
            field=models.SlugField(
                help_text="A url fragment that identifies this resource.  Must be globablly unique for all site files.  Use lower case, dashes, and numbers only.",
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
