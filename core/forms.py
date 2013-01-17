from django import forms
from core.models import Item, Tag


class ItemForm(forms.ModelForm):
	class Meta:
		model = Item
		widgets = {
            'content': forms.Textarea(),
        }

class TagForm(forms.ModelForm):
	class Meta:
		model = Tag

class LoginForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput())	
