from django.db import models

class Tag(models.Model):
	name = models.CharField(max_length=200)
	slug = models.CharField(max_length=200)
	added = models.DateField(auto_now=True)

	def __str__(self):
		return self.name

# Create your models here.
class Item(models.Model):
	title = models.CharField(max_length=200)
	content = models.CharField(max_length=10000)
	tags = models.ManyToManyField(Tag)
	added = models.DateField(auto_now=True)
