import requests
from forms import ImageForm

def index(request):
	if request.method == 'GET':
		return render('index.html')


def compare(request):
	if request.method == 'POST':
		url = request.GET.get('imgurl', None)
			if url:
				data = ImageForm(request.POST)
				
