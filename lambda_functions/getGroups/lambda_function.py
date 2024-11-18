import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def deserialize_groups(dynamodb_items):
    """deserializer = TypeDeserializer()
    return [
        {key: deserializer.deserialize(value) for key, value in item.items()}
        for item in dynamodb_items
    ]"""
    return[{
            'owner_name': item['owner_name']['S'],
            'owner': item['owner']['S'],
            'image_url': item['image_url']['S'],
            'description': item['description']['S'],                        
            'id': int(item['id']['N']), #
            'genres': item['genres']['S'],
            'name': item['name']['S'],
        }
        for item in dynamodb_items
    ]

def lambda_handler(event, context):
    try:
        response = dynamodb_client.scan(TableName='Groups')    
        print(response) # debug

        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            raise RuntimeError(f"Error {status_code}, dynamo operation failed")
        
        groups = deserialize_groups(response['Items'])

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS, GET'
            },
            'body': json.dumps({'groups': groups})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'Error': str(e)})
        }

