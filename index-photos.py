import json
import boto3
import os
from aws_requests_auth.aws_auth import AWSRequestsAuth
import time
from elasticsearch import Elasticsearch, RequestsHttpConnection
import requests
import io
import base64
from base64 import decodestring

def lambda_handler(event, context):
    S3_details=event['Records'][0]['s3']
    bucket=event['Records'][0]['s3']['bucket']['name']
    photo=event['Records'][0]['s3']['object']['key']
    timeStamp=time.time()
    s3_client = boto3.client('s3')
    object_metadata = s3_client.head_object(
        Bucket=bucket, Key=photo)
    print(object_metadata)
    s3_clientobj = s3_client.get_object(Bucket=bucket, Key=photo)
    body=s3_clientobj['Body'].read().decode('utf-8')
    image = base64.b64decode(body)    
    
    if "x-amz-meta-customlabels" in object_metadata["ResponseMetadata"]["HTTPHeaders"]:
        clabels = object_metadata["ResponseMetadata"]["HTTPHeaders"]["x-amz-meta-customlabels"].split(
            ",")
        for c_labels in clabels:
            c_labels = c_labels.strip()
            c_labels = c_labels.lower()
    
    response=s3_client.delete_object(Bucket=bucket,Key=photo)
    response=s3_client.put_object(Bucket=bucket, Body=image, Key=photo,ContentType='image/jpg')
    
    
    client=boto3.client('rekognition')
    response = client.detect_labels(
    Image={"S3Object": {
        "Bucket": bucket, "Name": photo}},
    MaxLabels=10,
    MinConfidence=80
    )
    
    
    labels=response['Labels']
    custom_labels=[]
    for label in labels:
        custom_labels.append(label['Name'])
    if clabels[0] not in custom_labels:
        custom_labels.append(clabels[0])
    print("CUSTOM LABELS PRINTED")    
    print(custom_labels)
   
    format={
        'objectKey':photo,
        'bucket':bucket,
        'createdTimeStamp':timeStamp,
        'labels':custom_labels
    }
    
    # host="vpc-photos-ghddqifc2rukl7a43ddozxbajm.us-east-1.es.amazonaws.com"
    
    # es_payload=json.dumps(format).encode("utf-8")
    # awsauth = AWSRequestsAuth(aws_access_key='arn:aws:lambda:us-east-1:770693421928:layer:Klayers-python38-elasticsearch:38',
    #                   aws_secret_access_key='BankkrogwB1v0U5A1VksE98dKRXbDjOP8K4o1+dI',
    #                   aws_host=host,
    #                   aws_region='us-east-1',
    #                   aws_service='es')
    
    # esClient = Elasticsearch(
    #     hosts=[{'host': host, 'port':444}],
    #     use_ssl=True,
    #     http_auth=awsauth,
    #     verify_certs=True,
    #     connection_class=RequestsHttpConnection)
        
    # temp=esClient.index(index='photos', doc_type='photo', body=format)
    # print(temp)
    print("FORMAT PRINTED")
    print(format)
    ELASTIC_SEARCH_ENDPOINT = "https://search-photos-vv7swtb4bch34s5crdc2a7d6d4.us-east-1.es.amazonaws.com/photos/photos"
    ES_USER = "hcelastic"
    ES_PASSWORD = "Hcelastic@2022"
    
    response = json.loads(requests.post(ELASTIC_SEARCH_ENDPOINT,
                                        auth=(ES_USER, ES_PASSWORD),
                                        headers={
                                            "Content-Type": "application/json"},
                                        data=json.dumps(format)).content.decode('utf-8'))
    
    print(response)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET',
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json.dumps("Image labels have been detected successfully!")
    }
