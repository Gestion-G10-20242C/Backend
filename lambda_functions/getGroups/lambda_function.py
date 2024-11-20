from decimal import Decimal
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

# COPYPASTED FUNCTION FROM GETUSERSBUGROUP LAMBDA.
def get_users_by_group(group_id: str):
    # Obtenemos los username's de los usuarios que pertenecen al grupo group_id
    """response = dynamodb_client.query(
        TableName='Members',
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'N': group_id}
        },
        ProjectionExpression='username'
    )"""
    response = dynamodb_client.scan(
        TableName='Members',
        FilterExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'N': group_id}
        },
        ProjectionExpression='username'
    )
    print(response) # debug

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        raise RuntimeError(f"Error {status_code}, dynamo operation failed")
    
    usernames = deserialize_usernames(response['Items'])

    #################
    # Ahora obtenemos la información de los usuarios que matchean con alguno de los usernames
    if len(usernames) > 0:
        keys = [{'username': {'S': username['username']}} for username in usernames]

        response = dynamodb_client.batch_get_item(
            RequestItems={
                'UserProfiles': {
                    'Keys': keys
                }
            }
        )

        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            raise RuntimeError(f"Error {status_code}, batch_get_item dynamo operation failed")
        
        # Formateamos los resultados
        deserializer = TypeDeserializer()        
        if 'Responses' in response and 'UserProfiles' in response['Responses']:
            items = response['Responses']['UserProfiles']  # Acceder a los ítems
            users = [
                {k: deserializer.deserialize(v) for k, v in item.items()}
                for item in items
            ]
        else:
            users = []
    else:
        users = []
    return users




def deserialize_groups(dynamodb_items):
    """deserializer = TypeDeserializer()
    return [
        {
            key: (int(deserializer.deserialize(value)) if isinstance(value, Decimal) else deserializer.deserialize(value))
            for key,value in item.items()
        }
        #{key: deserializer.deserialize(value) for key, value in item.items()}
        for item in dynamodb_items
    ]"""
    return[{
            'owner_name': item.get('owner_name', {}).get('S', ''),
            'owner': item.get('owner', {}).get('S', ''),
            'image_url': item.get('image_url', {}).get('S', ''),
            'description': item.get('description', {}).get('S', ''),
            'id': int(item['id']['N']), # id tiene que estar xq es clave de partición
            'genres': item.get('genres', {}).get('S', ''),
            'name': item.get('name', {}).get('S', '')
        }
        for item in dynamodb_items
    ]

def lambda_handler(event, context):
    try:
        response = dynamodb_client.scan(TableName='Groups')    

        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            raise RuntimeError(f"Error {status_code}, dynamo operation failed")
        
        if 'Items' in response:
            groups = deserialize_groups(response['Items'])
        else:
            groups = []

        # Add members of each group
        for group in groups:
            group['members'] = get_users_by_group(group['id'])

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

