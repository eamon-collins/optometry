import requests
import base64
from PIL import Image
import io
import json
import datetime
from clarifai.rest import ClarifaiApp
from watson_developer_cloud import VisualRecognitionV3
import boto3
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
      microsoft = 'Microsoft' in data.get('competitors')
      results = []
      if imgurl:
        #construct base64 and bytes encoded copies of image for services that can/need to use them
        image = requests.get(imgurl).content
        b64image = base64.b64encode(image)
        blobimage = bytes(image)

        clarifai_predict = ClarifaiApp()
        clarifai_resp = clarifai_predict.tag_urls(urls=[imgurl], model=clarifai_model)
        c = []
        for tag in clarifai_resp['outputs'][0]['data']['concepts']:
          c.append({'tag': tag['name'], 'score': tag['value']})
        results.append({'company':'Clarifai', 'tags': c,})

        #Google Cloud Vision handler
        if google:
          g = []
          #google_resp = json.loads(requests.post('https://vision.googleapis.com/v1/images:annotate?key='+GOOGLE_API_KEY, data=build_google(imgurl)).content)
          google_resp = {"responses": [{"labelAnnotations": [{"mid": "/m/01f4td","description": "rural area","score": 0.6766008},{"mid": "/m/01f4td","description": "norse","score": 0.5643342},]}]}
          for tag in google_resp['responses'][0]['labelAnnotations']:
            g.append({'tag': tag['description'], 'score': tag['score']})
          results.append({'company':'Google', 'tags': g})

        #IBM Visual Recognition handler
        if ibm:
          i = []
          ibm_predict = VisualRecognitionV3('2016-05-20', api_key= IBM_API_KEY)
          ibm_resp = ibm_predict.classify(images_url=imgurl)
          for tag in ibm_resp['images'][0]['classifiers'][0]['classes']:
            i.append({'tag': tag['class'], 'score': tag['score']})
          i = sorted(i, key=lambda tag: tag['score'], reverse=True)
          results.append({'company':'IBM', 'tags': i})

        #AWS Rekognition handler
        if amazon:
          a = []
          amazon_predict = boto3.client('rekognition', region_name='us-east-1')
          amazon_resp = amazon_predict.detect_labels(Image={'Bytes': blobimage}, MaxLabels=15)
          for tag in amazon_resp['Labels']:
            a.append({'tag': tag['Name'], 'score': tag['Confidence']})
          results.append({'company':'Amazon', 'tags': a})

        #Microsoft Computer Vision handler
        if microsoft:
          m = []
          microsoft_resp = build_microsoft(imgurl)
          for tag in microsoft_resp['tags']:
            m.append({'tag': tag['name'], 'score': tag['confidence']})
          results.append({'company': 'Microsoft', 'tags': m})

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

def build_microsoft(imgurl):
  headers = {'Ocp-Apim-Subscription-Key': MICROSOFT_API_KEY,
              'Content-Type': 'application/json'}
  params = {'language' : 'en',
            'visualFeatures': 'Tags'}
  data = json.dumps({'url': imgurl})
  resp = requests.post('https://eastus2.api.cognitive.microsoft.com/vision/v1.0/analyze', params=params, headers=headers, data=data)
  return json.loads(resp.content)

def build_amazon(b64image):
  endpoint = 'https://rekognition.us-east-1.amazonaws.com'
  now = datetime.datetime.utcnow()
  amz_date = now.strftime('%Y%m%dT%H%M%SZ')
  date = now.strftime('%Y%m%d')
  #authorization does not have signature attached, using boto3 instead
  authorization = 'AWS4-HMAC-SHA256' + ' ' + 'Credential=' + AMAZON_API_KEY_ID + '/' + date + '/us-east-1/rekognition/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature='
  headers = {'Content-Type': 'application/x-amz-json-1.1',
              'X-Amz-Date': amz_date,
              'X-Amz-Target': 'RekognitionService.DetectLabels',
              'Authorization': authorization}
  
  request_params = json.dumps({'Image':{'Bytes': b64image},
                              'MaxLabels':15})
  return json.loads(requests.post(endpoint, data=request_params, headers=headers).content)




