from django.db import models


class Node(models.Model):
    identifier = models.CharField(max_length=20, unique=True)
