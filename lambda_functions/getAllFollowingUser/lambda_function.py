import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    username = event['pathParameters']['username']

    response = dynamodb_client.query(
        TableName='Follows',
        KeyConditionExpression='username = :username',
        ExpressionAttributeValues={':username': {'S': username}}
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }

    items = response.get('Items', [])
    if not items:
        return {
            'statusCode': 200,
            'body': json.dumps([])
        }

    deserializer = TypeDeserializer()
    items = [{k: deserializer.deserialize(v) for k, v in item.items()} for item in items]
    return {
        'statusCode': 200,
        'body': json.dumps(items)
    }


event = {'resource': '/users/{username}/following', 'path': '/users/gabitest/following', 'httpMethod': 'GET', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Authorization': 'Bearer eyJraWQiOiI1VmxMdEZvU0VjczZoUGJmUmNjM3F4MEVHeVhpcXRHM2Zna0hPUzZMc2NrPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIyNDA4ZTQxOC0zMGYxLTcwZTItNzQ3Yi1hMTlhNGU1N2RiNzYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfMXI2RkRaeklkIiwiY29nbml0bzp1c2VybmFtZSI6ImdhYml0ZXN0Iiwib3JpZ2luX2p0aSI6IjE3NGE3ZmVkLTJjZjgtNDljNS05MmIxLWJmNjBlYjllM2VjMSIsImF1ZCI6IjJpN3Joc3ZvbzQzbnFibGsyaDh1Y3JmYTh2IiwiZXZlbnRfaWQiOiJjOGI4MDY0ZC1jNTU0LTRjZDctOWZlNy1kN2M2M2ZkMjRkN2YiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTczMDE2NTE2NSwiZXhwIjoxNzMwMTcyMzY1LCJpYXQiOjE3MzAxNjUxNjUsImp0aSI6ImI5MzE0YmE2LWM2ZTktNGM4YS1hN2IyLWFjMGNiOTkzOTYzOSIsImVtYWlsIjoiaXNub3RmYWtlbWFpbEBnbWFpbC5jb20ifQ.MfM5azJ0glujyA-Vwu5xQDsxEK75qyLK2Zcw8mxvDYObKSeywzKr0YFHh67N0TLm5AdCw7yJolVZx-j1heKs3NysqwPM3LQQ-IoVsFDVHkmGw2VDAjpQFva5t5xrKx7N60Gt32cH8z-1CQXfiGU6z46nwSl__EMfe3ln_-3GhcR2jx4PI7bC2-7MkeVw6r233P8tV44r9shIB1dOZsWPyAmxEcihfyOr27GeL9v4Dsp_xpD7eNzsyrSfWeIQznPg5NmJLaNVpUsDwkniWnfQoOHKAMShVxobm6xaTGpdk295nAUVJ9SMiR7tVJgfWS8ijDIR9l-T6O7DTOC7r4vUSw', 'Content-Type': 'application/json', 'Host': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'Postman-Token': '9d54537b-6fcf-4431-a5c3-0ada03173355', 'User-Agent': 'PostmanRuntime/7.42.0', 'X-Amzn-Trace-Id': 'Root=1-67203bd3-0fde7e17218856c36690eab4', 'X-Forwarded-For': '201.231.14.246', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'], 'Authorization': ['Bearer eyJraWQiOiI1VmxMdEZvU0VjczZoUGJmUmNjM3F4MEVHeVhpcXRHM2Zna0hPUzZMc2NrPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIyNDA4ZTQxOC0zMGYxLTcwZTItNzQ3Yi1hMTlhNGU1N2RiNzYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfMXI2RkRaeklkIiwiY29nbml0bzp1c2VybmFtZSI6ImdhYml0ZXN0Iiwib3JpZ2luX2p0aSI6IjE3NGE3ZmVkLTJjZjgtNDljNS05MmIxLWJmNjBlYjllM2VjMSIsImF1ZCI6IjJpN3Joc3ZvbzQzbnFibGsyaDh1Y3JmYTh2IiwiZXZlbnRfaWQiOiJjOGI4MDY0ZC1jNTU0LTRjZDctOWZlNy1kN2M2M2ZkMjRkN2YiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTczMDE2NTE2NSwiZXhwIjoxNzMwMTcyMzY1LCJpYXQiOjE3MzAxNjUxNjUsImp0aSI6ImI5MzE0YmE2LWM2ZTktNGM4YS1hN2IyLWFjMGNiOTkzOTYzOSIsImVtYWlsIjoiaXNub3RmYWtlbWFpbEBnbWFpbC5jb20ifQ.MfM5azJ0glujyA-Vwu5xQDsxEK75qyLK2Zcw8mxvDYObKSeywzKr0YFHh67N0TLm5AdCw7yJolVZx-j1heKs3NysqwPM3LQQ-IoVsFDVHkmGw2VDAjpQFva5t5xrKx7N60Gt32cH8z-1CQXfiGU6z46nwSl__EMfe3ln_-3GhcR2jx4PI7bC2-7MkeVw6r233P8tV44r9shIB1dOZsWPyAmxEcihfyOr27GeL9v4Dsp_xpD7eNzsyrSfWeIQznPg5NmJLaNVpUsDwkniWnfQoOHKAMShVxobm6xaTGpdk295nAUVJ9SMiR7tVJgfWS8ijDIR9l-T6O7DTOC7r4vUSw'], 'Content-Type': ['application/json'], 'Host': ['nev9ddp141.execute-api.us-east-1.amazonaws.com'], 'Postman-Token': ['9d54537b-6fcf-4431-a5c3-0ada03173355'], 'User-Agent': ['PostmanRuntime/7.42.0'], 'X-Amzn-Trace-Id': ['Root=1-67203bd3-0fde7e17218856c36690eab4'], 'X-Forwarded-For': ['201.231.14.246'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'username': 'gabitest'}, 'stageVariables': None, 'requestContext': {'resourceId': 'zyikwq', 'resourcePath': '/users/{username}/following', 'httpMethod': 'GET', 'extendedRequestId': 'AY5JJGJ7IAMEq7A=', 'requestTime': '29/Oct/2024:01:35:15 +0000', 'path': '/prod/users/gabitest/following', 'accountId': '349609960822', 'protocol': 'HTTP/1.1', 'stage': 'prod', 'domainPrefix': 'nev9ddp141', 'requestTimeEpoch': 1730165715790, 'requestId': '6c75e74c-d306-4b32-9c0e-2edd79432edc', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '201.231.14.246', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'PostmanRuntime/7.42.0', 'user': None}, 'domainName': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'deploymentId': 'tp1cso', 'apiId': 'nev9ddp141'}, 'body': '{\r\n    "name":"Gabi"\r\n}', 'isBase64Encoded': False}
print(lambda_handler(event, None))