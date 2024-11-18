import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def deserialize(dynamodb_items):
    deserializer = TypeDeserializer()
    return [
        {key: deserializer.deserialize(value) for key, value in item.items()}
        for item in dynamodb_items
    ]

def lambda_handler(event, context):
    
    response = dynamodb_client.scan(TableName='Groups')    
    print(response) # debug
    
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 500,
            'body': json.dumps('Error')
        }
    
    
    groups = deserialize(response['Items'])

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, GET'
        },
        'body': json.dumps({'groups': groups})
    }

