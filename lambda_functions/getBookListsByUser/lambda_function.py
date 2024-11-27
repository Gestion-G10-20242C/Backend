import ast
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal
import urllib.parse


dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')


def clean_dynamodb_item(dynamodb_item):
    """Transform DynamoDB items from DynamoDB JSON format to standard JSON."""
    deserializer = TypeDeserializer()
    return [
        {key: deserializer.deserialize(value) for key, value in item.items()}
        for item in dynamodb_item.get('Items', [])
    ]

def map_books(books):
    return [{'id': id_, 'image_url': image_url, 'title': title, 'isbn': isbn} 
            for id_, image_url, title, isbn in ast.literal_eval(books)]



def get_booklists_by_username(username):
    """Get booklists by username."""
    # Step 1: Query the Booklists table for items matching the username
    response = dynamodb_client.scan(
        TableName='Booklists',
        FilterExpression='username = :username',
        ExpressionAttributeValues={
            ':username': {'S': username}
        },
    )
    
    cleaned_response = clean_dynamodb_item(response)
    for item in cleaned_response:
        item['books'] = map_books(item['books'])
    return cleaned_response

def lambda_handler(event, context):
    print(event.get('pathParameters', {}))
    username = urllib.parse.unquote(event['pathParameters']['username'])


    try:
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS, GET'
            },
            'body': json.dumps(get_booklists_by_username(username))
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'Error': str(e)})
        }


# event = {
#     "pathParameters": {
#         "username": "gabitest"
#     }
# }
# print(lambda_handler(event, None))