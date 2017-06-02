import requests
from .forms import ImageForm
from django.shortcuts import render

def index(request):
    if request.method == 'GET':
        form = ImageForm()
        return render('index.html', {'form': form})


def compare(request):
    if request.method == 'POST':
        url = request.GET.get('imgurl', None)
        if url:
            data = ImageForm(request.POST)
            if data.imgurl:
                return

