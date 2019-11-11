# Generated by Django 2.2.2 on 2019-11-07 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0015_auto_20190815_1901'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Distribution',
            new_name='DistributionUpload',
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset_identifier', models.CharField(max_length=64)),
                ('file_name', models.CharField(max_length=800)),
                ('identifier', models.CharField(max_length=64)),
                ('catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Node',
                                              unique_for_date='uploaded_at')),
            ],
        ),
        migrations.AddField(
            model_name='distributionupload',
            name='distribution',
            field=models.ForeignKey(null=True,  # Placeholder, en la próxima migración lo seteamos a mano
                                    on_delete=django.db.models.deletion.CASCADE, to='catalog.Distribution'),
            preserve_default=False,
        ),
    ]