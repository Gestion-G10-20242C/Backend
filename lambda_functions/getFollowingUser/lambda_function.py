import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    username = event['username']
    user_following = event['following']

    response = dynamodb_client.get_item(
        TableName='Follows',
        Key={'username': {'S': username}, 'following': {'S': user_following}}
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }

    item = response.get('Item', {})
    if not item:
        return {
            'statusCode': 404,
            'body': json.dumps({'usernme': username, 'following': user_following, 'active': False})
        }

    deserializer = TypeDeserializer()
    item = {k: deserializer.deserialize(v) for k, v in item.items()}

    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }