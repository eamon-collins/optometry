import requests

def index(request):
	if request.method == 'GET':
		return render('index.html')


def compare(request):
	if request.method == 'POST':
		url = request.GET.get('imgurl', None)
			if url:
				google = request.POST.get('google', False)
				ibm = request.POST.get('ibm', False)
				amazon = request.POST.get('amazon', False)
				imagga = request.POST.get('imagga', False)