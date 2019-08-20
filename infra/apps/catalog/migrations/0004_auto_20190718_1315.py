# Generated by Django 2.2.2 on 2019-07-18 13:15

from django.db import migrations, models
import infra.apps.catalog.models.catalog_upload
import infra.apps.catalog.storage.catalog_storage


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_auto_20190718_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogupload',
            name='file',
            field=models.FileField(default=(b'#'), storage='infra.apps.catalog.storage.catalog_storage.CustomCatalogStorage', upload_to=infra.apps.catalog.models.catalog_upload.catalog_file_path),
            preserve_default=False,
        ),
    ]
