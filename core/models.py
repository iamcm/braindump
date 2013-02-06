from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save


class Tag(models.Model):
	name = models.CharField(max_length=200)
	slug = models.CharField(max_length=200)
	added = models.DateField(auto_now=True)

	def __str__(self):
		return self.name

	def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
		self.slug = self.name.lower().replace(' ','-')
		super(Tag, self).save(force_insert, force_update, using, update_fields)


class Item(models.Model):
	title = models.CharField(max_length=200)
	content = models.CharField(max_length=10000)
	tags = models.ManyToManyField(Tag)
	added = models.DateField(auto_now=True)


class BannedIP(models.Model):
	ip = models.IPAddressField(max_length=20)
	added = models.DateTimeField(auto_now=True)


class FailedLogin(models.Model):
	ip = models.IPAddressField(max_length=20)
	added = models.DateTimeField(auto_now=True)


##################
class User(AbstractUser):
	api_key = models.CharField(max_length=100)
##################