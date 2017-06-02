from django import forms

CLARIFAI_MODEL_CHOICES = (
	('general-v1.3','general-v1.3'),
	)

API_CHOICES = (
	('Google','Google'),
	('IBM','IBM'),
	('Amazon','Amazon'),
	)

class ImageForm(forms.Form):
	imgurl = forms.CharField(max_length=250)
	#image = forms.ImageField()
	clarifai_model = forms.ChoiceField(choices=CLARIFAI_MODEL_CHOICES)
	competitors = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=API_CHOICES)
