import json
import boto3

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    username = event['pathParameters']['username']
    body = json.loads(event['body'])
    print(f"Updating profile for username: {username} with data: {body}")

    update_expression = "SET "
    expression_attribute_values = {}
    expression_attribute_names = {}
    update_items = []

    for key, value in body.items():
        attribute_key = f"#{key}"
        expression_attribute_names[attribute_key] = key
        
        update_items.append(f"{attribute_key} = :{key}")
        expression_attribute_values[f":{key}"] = {'S': str(value)}

    update_expression += ", ".join(update_items)

    response = dynamodb_client.update_item(
        TableName='UserProfiles',
        Key={'username': {'S': username}},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names,
        ReturnValues="ALL_NEW"
    )
    
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }

    updated_profile = {k: v['S'] if 'S' in v else v['N'] for k, v in response['Attributes'].items()}
    return {
        'statusCode': 200,
        'body': json.dumps(updated_profile)
    }


#event = {'resource': '/users/{username+}', 'path': '/users/test123', 'httpMethod': 'POST', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'no-cache', 'Content-Type': 'application/json', 'Host': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'Postman-Token': 'b3e6de21-7bc5-4921-84ec-3ec2f7a6c20f', 'User-Agent': 'PostmanRuntime/7.42.0', 'X-Amzn-Trace-Id': 'Root=1-67184706-4f7f55a5764cef93285711e2', 'X-Forwarded-For': '54.86.50.139', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'], 'Cache-Control': ['no-cache'], 'Content-Type': ['application/json'], 'Host': ['nev9ddp141.execute-api.us-east-1.amazonaws.com'], 'Postman-Token': ['b3e6de21-7bc5-4921-84ec-3ec2f7a6c20f'], 'User-Agent': ['PostmanRuntime/7.42.0'], 'X-Amzn-Trace-Id': ['Root=1-67184706-4f7f55a5764cef93285711e2'], 'X-Forwarded-For': ['54.86.50.139'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'username': 'test123'}, 'stageVariables': None, 'requestContext': {'resourceId': 't2axqt', 'resourcePath': '/users/{username+}', 'httpMethod': 'POST', 'extendedRequestId': 'AFAJHEwzoAMEVIw=', 'requestTime': '23/Oct/2024:00:44:54 +0000', 'path': '/prod/users/test123', 'accountId': '349609960822', 'protocol': 'HTTP/1.1', 'stage': 'prod', 'domainPrefix': 'nev9ddp141', 'requestTimeEpoch': 1729644294705, 'requestId': '82802a2a-d6f1-4ff5-93ce-6ea717f8dd36', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '54.86.50.139', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'PostmanRuntime/7.42.0', 'user': None}, 'domainName': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'deploymentId': 'wbhg0r', 'apiId': 'nev9ddp141'}, 'body': '{\n    "name": "foo_updated",\n    "description": "probando update :)"\n}', 'isBase64Encoded': False}
#lambda_handler(event, {})