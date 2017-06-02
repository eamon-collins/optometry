import requests
import base64
from PIL import Image
import io
from clarifai.rest import ClarifaiApp
from django.shortcuts import render
from .forms import ImageForm
from secrets import *

def index(request):
  form = ImageForm()
  if request.method == 'GET':
    return render(request, 'index.html', {'form': form})

  elif request.method == 'POST':
    data = ImageForm(request.POST)
    if data.is_valid():
      data = data.cleaned_data
      imgurl = data.get('imgurl', False)
      clarifai_model = data.get('clarifai_model')
      google = 'Google' in data.get('competitors')
      ibm = 'IBM' in data.get('competitors')
      amazon = 'Amazon' in data.get('competitors')
      if imgurl:
        app = ClarifaiApp()
        c='working'#c = {'tags' : app.tag_urls(urls=[imgurl], model=clarifai_model)}

        # image = Image.open(io.BytesIO(requests.get(imgurl).content))
        # if image.width > 
        
        resp = None
        if google:
          resp = requests.post('https://vision.googleapis.com/v1/images:annotate?key='+GOOGLE_API_KEY, data=build_google(imgurl))
          print resp.content
          print resp.headers
          print resp.reason

        results = [
          {'company':'clarifai', 'tags': c,},
          {'company':'google', 'tags': resp,} 
        ]

        return render(request, 'index.html', {'form': form, 'results': results})


def build_google(imgurl):
  req = {
    "requests": [
      {
        "image":{
          "source":{
            "imageUri": imgurl
          }
        },
        "features":[
          {
            "type":"LABEL_DETECTION",
            "maxResults":1
          }
        ],
      },
    ],
  }
  return req