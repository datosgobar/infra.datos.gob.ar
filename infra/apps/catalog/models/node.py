from django.db import models


class Node(models.Model):
    identifier = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.identifier

    def get_latest_catalog_upload(self):
        return self.catalogupload_set.order_by('uploaded_at').last()
