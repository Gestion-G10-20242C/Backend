import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    username = event['pathParameters']['username']

    response = dynamodb_client.query(
        TableName='Follows',
        KeyConditionExpression='username = :username',
        FilterExpression='active = :active',
        ExpressionAttributeValues={
            ':username': {'S': username},
            ':active': {'BOOL': True}
        }
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
            'statusCode': 200,
            'body': json.dumps([])
        }

    deserializer = TypeDeserializer()
    items = [{k: deserializer.deserialize(v) for k, v in item.items()} for item in items]
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, GET'
        },            
        'body': json.dumps(items)
    }
