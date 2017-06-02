import requests
import base64
from PIL import Image
import io
import json
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
        clarifai_predict = ClarifaiApp()
        c='working'#c = {'tags' : clarifai_predict.tag_urls(urls=[imgurl], model=clarifai_model)}

        # image = Image.open(io.BytesIO(requests.get(imgurl).content))
        # if image.width > 
        
        g_resp = None
        i_resp = None
        if google:
          g_resp = 'working' #resp = requests.post('https://vision.googleapis.com/v1/images:annotate?key='+GOOGLE_API_KEY, data=build_google(imgurl))
        if ibm:
          i_resp = 

        results = [
          {'company':'Clarifai', 'tags': c,},
          {'company':'Google', 'tags': g_resp,},
          {'company':'IBM', 'tags': i_resp,},
        ]

        return render(request, 'index.html', {'form': form, 'results': results})


def build_google(imgurl):
  req_list = [
    {
      "image":{
        "source":{
          "imageUri": imgurl
        }
      },
      "features":[
        {
          "type":"LABEL_DETECTION",
          "maxResults":20
        }
      ]
    }
  ] 
  req = json.dumps({'requests': req_list})
  return req