import json

def lambda_handler(event, context):
#    print(event) #
    # holaaa :)
    username = event['pathParameters']['username']
    print(username)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


#event = {'resource': '/users/{username+}', 'path': '/users/test1234', 'httpMethod': 'GET', 'headers': {'Accept': '*/*', 'Host': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'User-Agent': 'curl/7.71.1', 'X-Amzn-Trace-Id': 'Root=1-67182807-112e0a7d55068e397cd2b8c0', 'X-Forwarded-For': '181.20.75.76', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Host': ['nev9ddp141.execute-api.us-east-1.amazonaws.com'], 'User-Agent': ['curl/7.71.1'], 'X-Amzn-Trace-Id': ['Root=1-67182807-112e0a7d55068e397cd2b8c0'], 'X-Forwarded-For': ['181.20.75.76'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'username': 'test1234'}, 'stageVariables': None, 'requestContext': {'resourceId': 't2axqt', 'resourcePath': '/users/{username+}', 'httpMethod': 'GET', 'extendedRequestId': 'AEsxRGSEIAMEQGw=', 'requestTime': '22/Oct/2024:22:32:39 +0000', 'path': '/prod/users/test1234', 'accountId': '349609960822', 'protocol': 'HTTP/1.1', 'stage': 'prod', 'domainPrefix': 'nev9ddp141', 'requestTimeEpoch': 1729636359763, 'requestId': 'eae661f5-2fa4-4997-b0c7-607c3f6a852f', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '181.20.75.76', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'curl/7.71.1', 'user': None}, 'domainName': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'deploymentId': 'bf3gso', 'apiId': 'nev9ddp141'}, 'body': None, 'isBase64Encoded': False}

#lambda_handler(event, {})