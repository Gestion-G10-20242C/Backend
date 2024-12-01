import json
import boto3
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Chats')

def addCORSHeader(response):
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS, GET'
    }
    return response

def lambda_handler(event, context):
    try: 
        username = event['pathParameters']['username']
        response = table.scan(
            FilterExpression='username = :id',
            ExpressionAttributeValues={
                ':id': username
            }
        )

        return addCORSHeader({
            'statusCode': 200,
            'body': json.dumps(response['Items'])
        })
    
    except Exception as e:
        return addCORSHeader({
            'statusCode': 400,
            'body': json.dumps(str(e))
        })

# print(lambda_handler({'pathParameters': {'username': 'gabitest'}}, None))