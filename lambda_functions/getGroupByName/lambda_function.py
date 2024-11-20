import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

"""
Lambda function to retrieve a group profile from a DynamoDB table.
Parameters:
event (dict): The event dictionary containing request parameters.
    - pathParameters (dict): Dictionary containing path parameters.
        - groupname (str): The name of the group profile to retrieve.
Returns:
dict: A dictionary containing the HTTP status code and the response body.
    - statusCode (int): The HTTP status code of the response.
    - body (str): The JSON-encoded response body.
        - On success: JSON-encoded group profile.
        - On failure: JSON-encoded error message.
"""
def lambda_handler(event, context):
    groupname = event['pathParameters']['groupname']
    print(groupname)
    
    response = dynamodb_client.get_item(
        TableName='Groups',
        Key={
            'groupname': {
                'S': groupname
            }
        }
    )
    
    # Verificación del estado de la respuesta
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps('Error: Group not found')
        }
    
    deserializer = TypeDeserializer()
    group_profile = {k: deserializer.deserialize(v) for k, v in response['Item'].items()}
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, GET'
        },
        'body': json.dumps(group_profile)
    }
