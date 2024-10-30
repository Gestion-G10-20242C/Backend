import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

"""
Lambda function to retrieve a user profile from a DynamoDB table.
Parameters:
event (dict): The event dictionary containing request parameters.
    - pathParameters (dict): Dictionary containing path parameters.
        - username (str): The username of the user profile to retrieve.
Returns:
dict: A dictionary containing the HTTP status code and the response body.
    - statusCode (int): The HTTP status code of the response.
    - body (str): The JSON-encoded response body.
        - On success: JSON-encoded user profile.
        - On failure: JSON-encoded error message.
"""
def lambda_handler(event, context):
    username = event['pathParameters']['username']
    print(username)
    
    response = dynamodb_client.get_item(
        TableName='UserProfiles',
        Key={
            'username': {
                'S': username
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
            'body': json.dumps('Error: Perfil no encontrado')
        }
    
    deserializer = TypeDeserializer()
    profile = {k: deserializer.deserialize(v) for k, v in response['Item'].items()}
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, GET'
        },
        'body': json.dumps(profile)
    }


###
# For local testing:
#event = {'resource': '/users/{username+}', 'path': '/users/test1234', 'httpMethod': 'GET', 'headers': {'Accept': '*/*', 'Host': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'User-Agent': 'curl/7.71.1', 'X-Amzn-Trace-Id': 'Root=1-67182807-112e0a7d55068e397cd2b8c0', 'X-Forwarded-For': '181.20.75.76', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Host': ['nev9ddp141.execute-api.us-east-1.amazonaws.com'], 'User-Agent': ['curl/7.71.1'], 'X-Amzn-Trace-Id': ['Root=1-67182807-112e0a7d55068e397cd2b8c0'], 'X-Forwarded-For': ['181.20.75.76'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'username': 'test1234'}, 'stageVariables': None, 'requestContext': {'resourceId': 't2axqt', 'resourcePath': '/users/{username+}', 'httpMethod': 'GET', 'extendedRequestId': 'AEsxRGSEIAMEQGw=', 'requestTime': '22/Oct/2024:22:32:39 +0000', 'path': '/prod/users/test1234', 'accountId': '349609960822', 'protocol': 'HTTP/1.1', 'stage': 'prod', 'domainPrefix': 'nev9ddp141', 'requestTimeEpoch': 1729636359763, 'requestId': 'eae661f5-2fa4-4997-b0c7-607c3f6a852f', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '181.20.75.76', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'curl/7.71.1', 'user': None}, 'domainName': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'deploymentId': 'bf3gso', 'apiId': 'nev9ddp141'}, 'body': None, 'isBase64Encoded': False}
#print("User:", lambda_handler(event, {}))