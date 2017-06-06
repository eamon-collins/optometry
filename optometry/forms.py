from django import forms

CLARIFAI_MODEL_CHOICES = (
	('general-v1.3','General'),
	('travel-v1.0','Travel'),
	('food-items-v1.0','Food'),
	('nsfw-v1.0','NSFW'),
	)

API_CHOICES = (
	('Google','Google'),
	('IBM','IBM'),
	('Amazon','Amazon'),
	('Microsoft','Microsoft')
	)

class ImageForm(forms.Form):
	layout_test = forms.BooleanField(required=False, initial=True)
	imgurl = forms.CharField(required=False, max_length=250)
	#image = forms.ImageField()
	clarifai_model = forms.ChoiceField(choices=CLARIFAI_MODEL_CHOICES)
	competitors = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=API_CHOICES)
