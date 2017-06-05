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

      #if layout test is checked, return requested tables with preset, fake data
      layout_test = data.get('layout_test')
      if layout_test:
        return render(request, 'index.html', {'form': form, 'results': layout_test_data(google, ibm, amazon, microsoft)})

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
          google_resp = json.loads(requests.post('https://vision.googleapis.com/v1/images:annotate?key='+GOOGLE_API_KEY, data=build_google(imgurl)).content)
          #google_resp = {"responses": [{"labelAnnotations": [{"mid": "/m/01f4td","description": "rural area","score": 0.6766008},{"mid": "/m/01f4td","description": "norse","score": 0.5643342},]}]}
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
        
        f = open('sample_output.txt', 'w')
        f.write(repr(results))
        f.close()

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


def layout_test_data(google, ibm, amazon, microsoft):
  results = []
  results.append({'company': 'Clarifai', 'tags': [{'tag': u'summer', 'score': 0.98168695}, {'tag': u'nature', 'score': 0.97212166}, {'tag': u'farm', 'score': 0.9689047}, {'tag': u'grass', 'score': 0.95977676}, {'tag': u'outdoors', 'score': 0.9521229}, {'tag': u'field', 'score': 0.9091958}, {'tag': u'rural', 'score': 0.9091601}, {'tag': u'leisure', 'score': 0.8994857}, {'tag': u'pasture', 'score': 0.8972074}, {'tag': u'family', 'score': 0.89348996}, {'tag': u'agriculture', 'score': 0.8800632}, {'tag': u'beautiful', 'score': 0.87906086}, {'tag': u'outside', 'score': 0.8564824}, {'tag': u'countryside', 'score': 0.85345554}, {'tag': u'young', 'score': 0.85037076}, {'tag': u'one', 'score': 0.84531885}, {'tag': u'hayfield', 'score': 0.8412552}, {'tag': u'mammal', 'score': 0.8277488}, {'tag': u'tree', 'score': 0.8218796}, {'tag': u'flower', 'score': 0.80977535}]})
  if google:
    results.append({'company': 'Google', 'tags': [{'tag': u'rural area', 'score': 0.6766008}, {'tag': u'farm', 'score': 0.6482424}, {'tag': u'meadow', 'score': 0.59396565}, {'tag': u'horse like mammal', 'score': 0.51159537}]})
  if ibm:
    results.append({'company': 'IBM', 'tags': [{'tag': u'green color', 'score': 0.963}, {'tag': u'animal', 'score': 0.765}, {'tag': u'mammal', 'score': 0.653}, {'tag': u'domestic animal', 'score': 0.653}, {'tag': u'dog', 'score': 0.652}, {'tag': u'ruminant', 'score': 0.603}, {'tag': u'deer', 'score': 0.602}, {'tag': u'vizsla dog', 'score': 0.569}, {'tag': u'Great Dane dog', 'score': 0.558}, {'tag': u'person', 'score': 0.55}, {'tag': u'boy at farm', 'score': 0.549}, {'tag': u'palomino horse', 'score': 0.53}]})
  if amazon:
    results.append({'company': 'Amazon', 'tags': [{'tag': u'Human', 'score': 99.30406951904297}, {'tag': u'People', 'score': 99.30635070800781}, {'tag': u'Person', 'score': 99.30635070800781}, {'tag': u'Backyard', 'score': 77.3866958618164}, {'tag': u'Yard', 'score': 77.3866958618164}, {'tag': u'Ivy', 'score': 76.58114624023438}, {'tag': u'Plant', 'score': 76.58114624023438}, {'tag': u'Vine', 'score': 76.58114624023438}, {'tag': u'Shorts', 'score': 75.4872055053711}, {'tag': u'Blossom', 'score': 67.45735168457031}, {'tag': u'Flora', 'score': 67.45735168457031}, {'tag': u'Flower', 'score': 67.45735168457031}, {'tag': u'Herbal', 'score': 63.904659271240234}, {'tag': u'Herbs', 'score': 63.904659271240234}, {'tag': u'Planter', 'score': 63.904659271240234}]})
  if microsoft:
    results.append({'company': 'Microsoft', 'tags': [{'tag': u'tree', 'score': 0.9998617172241211}, {'tag': u'outdoor', 'score': 0.999527096748352}, {'tag': u'grass', 'score': 0.9965176582336426}, {'tag': u'standing', 'score': 0.8547968864440918}, {'tag': u'house', 'score': 0.4055963158607483}]})
  return results

