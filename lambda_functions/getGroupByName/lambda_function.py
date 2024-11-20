from decimal import Decimal
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def deserialize_groups(dynamodb_items):
    return [{
            'owner_name': item.get('owner_name', {}).get('S', ''),
            'owner': item.get('owner', {}).get('S', ''),
            'image_url': item.get('image_url', {}).get('S', ''),
            'description': item.get('description', {}).get('S', ''),
            'id': int(item['id']['N']), # id has to be present because it's the partition key
            'genres': item.get('genres', {}).get('S', ''),
            'name': item.get('name', {}).get('S', '')
        }
        for item in dynamodb_items
    ]

def lambda_handler(event, context):
    try:
        # Get the group name from the query string parameters
        group_name = event.get('queryStringParameters', {}).get('name', None)
        
        if not group_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'Error': 'Group name must be provided'})
            }
        
        # Perform a query operation using the group name as the key
        response = dynamodb_client.query(
            TableName='Groups',
            KeyConditionExpression='name = :name',
            ExpressionAttributeValues={
                ':name': {'S': group_name}
            }
        )

        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            raise RuntimeError(f"Error {status_code}, DynamoDB query operation failed")
        
        if 'Items' in response:
            groups = deserialize_groups(response['Items'])
        else:
            groups = []

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
