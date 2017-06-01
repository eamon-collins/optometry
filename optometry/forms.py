from django import forms

class ImageForm(forms.Form):
	imgurl = forms.CharField(max_length=250)
	image = forms.ImageField()
	compares = forms.MultipleChoiceField(choices=['Google', 'IBM', 'Amazon'])