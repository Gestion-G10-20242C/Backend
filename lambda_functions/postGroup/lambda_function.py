import base64
import json
import time
import boto3

MILIS = 1000
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def addCORSHeader(response):
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS, POST'
    }
    return response

def fetchOwnerName(username):
    response = dynamodb_client.get_item(
        TableName='UserProfiles',
        Key={
            'username': {'S': username}
        }
    )

    item = response.get('Item', {})
    return item.get('name', {}).get('S', '')

def clean_dynamodb_item(dynamodb_item):
    """Transform DynamoDB item format to standard JSON."""
    return {key: list(value.values())[0] for key, value in dynamodb_item.items()}



def lambda_handler(event, context):
    username = event['pathParameters']['username']
    body = json.loads(event['body'])

    existing_group_response = dynamodb_client.scan(
        TableName='Groups',
        FilterExpression='#group_name = :group_name',
        ExpressionAttributeNames={
            '#group_name': 'name'
        },
        ExpressionAttributeValues={
            ':group_name': {'S': body['name']}
        }
    )

    if existing_group_response.get('Items'):
        return addCORSHeader({
            'statusCode': 400,
            'body': json.dumps('Error: Group already exists')
        })

    item = {
        'id': {'N': str(int(time.time() * MILIS))},
        'owner': {'S': username},
        'owner_name': {'S': fetchOwnerName(username)},
    }


    if 'description' in body:
        body['description'] = base64.b64encode(body['description'].encode()).decode()

    for key, value in body.items():
        item[key] = {'S': str(value)}


    print(item)
    
    response = dynamodb_client.put_item(
       TableName='Groups',
       Item=item
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return addCORSHeader({
            'statusCode': 400,
            'body': json.dumps('Error')
        })



    return addCORSHeader({
        'statusCode': 200,
        'body': json.dumps(clean_dynamodb_item(item))
    })
# event = {
#     'pathParameters': {'username': 'gabitest'},
#     'body': '{"description": "El mejor grupo del mundo", "image_url":"https://i.pinimg.com/736x/f8/77/11/f8771136acc302740ba301d51d39cf7a.jpg", "genres": "Gabigol"}'
# }
# lambda_handler(event, None) 