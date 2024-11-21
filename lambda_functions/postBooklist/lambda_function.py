from boto3.dynamodb.conditions import Attr
import boto3
import json

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def clean_dynamodb_item(dynamodb_item):
    """Transform DynamoDB item format to standard JSON."""
    return {key: list(value.values())[0] for key, value in dynamodb_item.items()}

def add_cors_headers(response):
    """Add CORS headers to response."""
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS, POST'
    }

    return response


def lambda_handler(event, context):
    username = event['pathParameters']['username']
    body = json.loads(event['body'])

    item = {
        'username': {'S': username},
        'name': {'S': body['name']},
        'books': {'S': json.dumps(body.get('books', []))}
    }

    response = dynamodb_client.put_item(
        TableName='Booklists',
        Item=item,
        ConditionExpression='attribute_not_exists(username) AND attribute_not_exists(#name)',
        ExpressionAttributeNames={
            '#name': 'name' 
        }
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
       return add_cors_headers({
           'statusCode': 400,
           'body': json.dumps('Error')
       })


    return add_cors_headers({
        'statusCode': 200,
        'body': json.dumps(clean_dynamodb_item(item))
    })

# event = {
#     'pathParameters': {'username': 'gabitest'},
#     'body': '{"name":"En espera"}'
# }
# print(lambda_handler(event, None))