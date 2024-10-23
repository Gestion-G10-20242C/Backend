import json
import boto3

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

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

    print(response)
    # Checkeo que haya funcionado el get
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }
    
    if 'Item' not in response: # (xq devuelve 200)
        return {
            'statusCode': 404,
            'body': json.dumps('Error: Perfil no encontrado')
        }

    # Obtengo los datos del perfil, que en la response están con su tipo de dato
    item = response['Item']
    profile = {
        'username': item['username']['S'],
        'name': item['name']['S'],
        'description': item['description']['S'] if 'description' in item else 'Me he creado una cuenta en ReadMe :)'
    }

    return {
        'statusCode': 200,
        'body': json.dumps(profile)
    }


###
# For local testing:
#event = {'resource': '/users/{username+}', 'path': '/users/test1234', 'httpMethod': 'GET', 'headers': {'Accept': '*/*', 'Host': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'User-Agent': 'curl/7.71.1', 'X-Amzn-Trace-Id': 'Root=1-67182807-112e0a7d55068e397cd2b8c0', 'X-Forwarded-For': '181.20.75.76', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Host': ['nev9ddp141.execute-api.us-east-1.amazonaws.com'], 'User-Agent': ['curl/7.71.1'], 'X-Amzn-Trace-Id': ['Root=1-67182807-112e0a7d55068e397cd2b8c0'], 'X-Forwarded-For': ['181.20.75.76'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'username': 'test1234'}, 'stageVariables': None, 'requestContext': {'resourceId': 't2axqt', 'resourcePath': '/users/{username+}', 'httpMethod': 'GET', 'extendedRequestId': 'AEsxRGSEIAMEQGw=', 'requestTime': '22/Oct/2024:22:32:39 +0000', 'path': '/prod/users/test1234', 'accountId': '349609960822', 'protocol': 'HTTP/1.1', 'stage': 'prod', 'domainPrefix': 'nev9ddp141', 'requestTimeEpoch': 1729636359763, 'requestId': 'eae661f5-2fa4-4997-b0c7-607c3f6a852f', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '181.20.75.76', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'curl/7.71.1', 'user': None}, 'domainName': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'deploymentId': 'bf3gso', 'apiId': 'nev9ddp141'}, 'body': None, 'isBase64Encoded': False}
#lambda_handler(event, {})