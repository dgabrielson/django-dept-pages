# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("unitpages", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="sitefile",
            name="slug",
            field=models.SlugField(
                primary_key=True,
                serialize=False,
                help_text=b"A url fragment that identifies this resource.  Must be globablly unique for all site files.  Use lower case, dashes, and numbers only.",
                unique=True,
            ),
            preserve_default=True,
        )
    ]
