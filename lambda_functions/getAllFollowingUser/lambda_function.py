import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    username = event['username']

    response = dynamodb_client.query(
        TableName='Follows',
        KeyConditionExpression='username = :username',
        ExpressionAttributeValues={':username': {'S': username}}
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }

    items = response.get('Items', [])
    if not items:
        return {
            'statusCode': 404,
            'error': 'No following users found',
            'body': json.dumps([])
        }

    deserializer = TypeDeserializer()
    items = [{k: deserializer.deserialize(v) for k, v in item.items()} for item in items]
    return {
        'statusCode': 200,
        'body': json.dumps(items)
    }
