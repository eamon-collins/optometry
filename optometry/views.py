import requests
import base64
from PIL import Image
import io
import json
from clarifai.rest import ClarifaiApp
from watson_developer_cloud import VisualRecognitionV3
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
      results = []
      if imgurl:
        # clarifai_predict = ClarifaiApp()
        # clarifai_resp = clarifai_predict.tag_urls(urls=[imgurl], model=clarifai_model)
        # c = []
        # for tag in clarifai_resp['outputs'][0]['data']['concepts']:
        #   c.append({'tag': tag['name'], 'score': tag['value']})
        # results.append({'company':'Clarifai', 'tags': c,})


        if google:
          g = []
          google_resp = json.loads(requests.post('https://vision.googleapis.com/v1/images:annotate?key='+GOOGLE_API_KEY, data=build_google(imgurl)).content)
          for tag in google_resp['responses'][0]['labelAnnotations']:
            g.append({'tag': tag['description'], 'score': tag['score']})
          results.append({'company':'Google', 'tags': g})
        if ibm:
          i = []
          ibm_predict = VisualRecognitionV3('2016-05-20', api_key= IBM_API_KEY)
          ibm_resp = ibm_predict.classify(images_url=imgurl)
          for tag in ibm_resp['images'][0]['classifiers'][0]['classes']:
            i.append({'tag': tag['class'], 'score': tag['score']})
          i = sorted(i, key=lambda tag: tag['score'], reverse=True)
          results.append({'company':'IBM', 'tags': i})
        if amazon:
          

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