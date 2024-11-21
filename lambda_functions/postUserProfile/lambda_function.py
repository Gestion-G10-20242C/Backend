import json
import boto3

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')

"""
Lambda function to handle user profile creation.
This function extracts the username from the path parameters and the user profile details from the request body.
It then inserts the user profile into the 'UserProfiles' DynamoDB table.
Parameters:
event (dict): The event dictionary containing request data.
    - pathParameters (dict): Contains the 'username' key.
    - body (str): JSON string containing the user profile details.
Returns:
dict: A dictionary containing the status code and response body.
    - statusCode (int): HTTP status code indicating the result of the operation.
    - body (str): JSON string containing the response message.
"""
def lambda_handler(event, context):
    username = event['pathParameters']['username']
    body = json.loads(event['body'])

    item = {}
    item['username'] = {'S': username}

    for key, value in body.items():
        item[key] = {'S': str(value)}

    # Inserto a la bdd de perfiles
    response = dynamodb_client.put_item(
        TableName='UserProfiles',
        Item=item
    )

    lambda_client.invoke(
        FunctionName='postBooklist',
        InvocationType='Event',
        Payload=json.dumps({
            'pathParameters': {
                'username': username
            },
            'body': json.dumps({
                'name': 'Leidos'
            })
        })
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
        'body': json.dumps(body)
    }

##
#For local testing:
# event = {'resource': '/users/{username+}', 'path': '/users/test123', 'httpMethod': 'POST', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'no-cache', 'Content-Type': 'application/json', 'Host': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'Postman-Token': 'b3e6de21-7bc5-4921-84ec-3ec2f7a6c20f', 'User-Agent': 'PostmanRuntime/7.42.0', 'X-Amzn-Trace-Id': 'Root=1-67184706-4f7f55a5764cef93285711e2', 'X-Forwarded-For': '54.86.50.139', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'], 'Cache-Control': ['no-cache'], 'Content-Type': ['application/json'], 'Host': ['nev9ddp141.execute-api.us-east-1.amazonaws.com'], 'Postman-Token': ['b3e6de21-7bc5-4921-84ec-3ec2f7a6c20f'], 'User-Agent': ['PostmanRuntime/7.42.0'], 'X-Amzn-Trace-Id': ['Root=1-67184706-4f7f55a5764cef93285711e2'], 'X-Forwarded-For': ['54.86.50.139'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'username': 'test123'}, 'stageVariables': None, 'requestContext': {'resourceId': 't2axqt', 'resourcePath': '/users/{username+}', 'httpMethod': 'POST', 'extendedRequestId': 'AFAJHEwzoAMEVIw=', 'requestTime': '23/Oct/2024:00:44:54 +0000', 'path': '/prod/users/test123', 'accountId': '349609960822', 'protocol': 'HTTP/1.1', 'stage': 'prod', 'domainPrefix': 'nev9ddp141', 'requestTimeEpoch': 1729644294705, 'requestId': '82802a2a-d6f1-4ff5-93ce-6ea717f8dd36', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '54.86.50.139', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'PostmanRuntime/7.42.0', 'user': None}, 'domainName': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'deploymentId': 'wbhg0r', 'apiId': 'nev9ddp141'}, 'body': '{\n    "name": "foo",\n    "description": "probando readme :)"\n}', 'isBase64Encoded': False}
# lambda_handler(event, {})