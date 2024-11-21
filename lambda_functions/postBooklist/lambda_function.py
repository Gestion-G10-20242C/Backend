from boto3.dynamodb.conditions import Attr
import boto3
import json

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def clean_dynamodb_item(dynamodb_item):
    """Transform DynamoDB item format to standard JSON."""
    return {key: list(value.values())[0] for key, value in dynamodb_item.items()}

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
       return {
           'statusCode': 400,
           'body': json.dumps('Error')
       }


    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, POST'
        },
        'body': json.dumps(clean_dynamodb_item(item))
    }

# event = {
#     'pathParameters': {'username': 'gabitest'},
#     'body': '{"name":"Leidos"}'
# }
# print(lambda_handler(event, None))