from decimal import Decimal
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def deserialize_groups(dynamodb_items):
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

def deserialize_users(dynamodb_items):
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

def deserialize_group_ids(dynamodb_items):
    return[{
            #'username': item['username']['S'],            
            'id': int(item['id']['N']), #
        }
        for item in dynamodb_items
    ]

def lambda_handler(event, context):
    try:
        print(event)
        username = event['pathParameters']['username']

        # Obtenemos los group_id's de los grupos a los que pertenece usuario username
        """response = dynamodb_client.query(
            TableName='Members',
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={
                ':username': {'S': username}
            },
            ProjectionExpression='id'
        )"""
        response = dynamodb_client.scan(
            TableName='Members',
            FilterExpression='username = :username',
            ExpressionAttributeValues={
                ':username': {'S': username}
            },
            ProjectionExpression='id'
        )
        print(response) # debug

        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            raise RuntimeError(f"Error {status_code}, dynamo operation failed")
        
        group_ids = deserialize_group_ids(response['Items'])

        #################

        # Ahora obtenemos la información de los grupos que matchean con alguno de los group_ids
        keys = [{'id': {'N': str(group_id['id'])}} for group_id in group_ids]

        response = dynamodb_client.batch_get_item(
            RequestItems={
                'Groups': {
                    'Keys': keys
                }
            }
        )

        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            raise RuntimeError(f"Error {status_code}, batch_get_item dynamo operation failed")

        print(f"batch_get_item: {response}")
        groups = deserialize_groups(response['Responses']['Groups'])

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