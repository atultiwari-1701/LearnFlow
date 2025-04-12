from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()