import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
import requests
import urllib.parse
# from aws_requests_auth.aws_auth import AWSRequestsAuth
# from elasticsearch import Elasticsearch, RequestsHttpConnection
import random

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

headers = { "Content-Type": "application/json" }
region = 'us-east-1'
lex = boto3.client('lex-runtime', region_name=region)

ELASTIC_SEARCH_ENDPOINT = "https://search-photos-vv7swtb4bch34s5crdc2a7d6d4.us-east-1.es.amazonaws.com/photos/photos/_search"
ES_USER = "hcelastic"
ES_PASSWORD = "Hcelastic@2022"

def lambda_handler(event, context):
    # q1 = event["queryStringParameters"]["q"]
    # labels = get_labels(q1)
    print("enevent should get printed now")
    
    print(event)
    q1 = event["queryStringParameters"]["q"]
    print(q1)
    # return q1
    labels = get_labels(q1)

    print(labels)
    
    if len(labels) != 0:
        img_paths = get_photo_path(labels)
    
    
    
    if not img_paths:
        return{
            'statusCode':200,
            "headers": {"Access-Control-Allow-Origin":"*"},
            'body': json.dumps('No Results found')
        }
    else:    
        return{
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin":"*"},
            'body': json.dumps(img_paths),
            #     {
            #     'imagePaths':img_paths,
            #     'userQuery':q1,
            #     'labels': labels,
            # },
            'isBase64Encoded': False
        }
    
def get_labels(query):
    sample_string = 'pqrstuvwxyabdsfbc'
    userid = ''.join((random.choice(sample_string)) for x in range(8))
    
    response = lex.post_text(
        botName='photobot',                 
        botAlias='photobotalias',
        userId=userid,           
        inputText=query
    )
    print("lex-response", response)
    
    labels = []
    if 'slots' not in response:
        print("No photo collection for query {}".format(query))
    else:
        print ("slot: ",response['slots'])
        slot_val = response['slots']
        for key,value in slot_val.items():
            if value!=None:
                labels.append(value)
    return labels

    
def get_photo_path(keys):

        
    resp = []
    for key in keys:
        if (key is not None) and key != '':
            # searchData = es.search({"query": {"match": {"labels": key}}})
            
            es_query = {
            "query": {
                "match": {
                    "labels": key
                    }
                }
            }
            es = json.loads(requests.get(ELASTIC_SEARCH_ENDPOINT,
                                              auth=(ES_USER, ES_PASSWORD),
                                              headers={
                                                  "Content-Type": "application/json"},
                                              data=json.dumps(es_query)).content.decode('utf-8'))
            resp.append(es)
    print(resp)
    
    

    output = []
    for r in resp:
        if 'hits' in r:
             for val in r['hits']['hits']:
                key = val['_source']['objectKey']
                if key not in output:
                    output.append('https://b2photoss.s3.amazonaws.com/'+key)
    print (output)
    return output