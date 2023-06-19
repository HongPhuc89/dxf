from django.db import models
from django.conf import settings


# Create your models here.


class FileModel(models.Model):
    file_field = models.FileField(upload_to="uploaded/")
    cred_file_field = models.FileField(upload_to="uploaded/")


class SavedModel(models.Model):
    web_address = models.CharField(max_length=100)
    original_text = models.CharField(max_length=10000)
    translated_text = models.CharField(max_length=10000)
    link_name = models.CharField(max_length=1000, default=".png")
    link = models.URLField(null=True)


class InterSavedModel(models.Model):
    web_address = models.CharField(max_length=100)
    original_text = models.CharField(max_length=10000)
    translated_text = models.CharField(max_length=10000)
    link_name = models.CharField(max_length=1000, default=".png")
    # image = models.ImageField(upload_to="screenshots/permanent/")
    image = models.URLField()
    link = models.URLField(null=True)
