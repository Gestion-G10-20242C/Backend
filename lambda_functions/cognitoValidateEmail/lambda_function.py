import json
import boto3
import os
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')

CLIENT_ID = os.environ.get('CLIENT_ID')
USER_POOL_ID = os.environ.get('USER_POOL_ID')

def lambda_handler(event, context):
    username = event['username']
    password = event['password']
    confirmation_code = event['confirmation_code']
    
    try:
        cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            ConfirmationCode=confirmation_code
        )

        lambda_client.invoke(
            FunctionName='postUserProfile',
            InvocationType='Event',
            Payload=json.dumps({'pathParameters': {'username': username}, 'body': '{}'})
        )
        
        response = lambda_client.invoke(
            FunctionName='cognitoAuthenticateUser',
            InvocationType='RequestResponse',
            Payload=json.dumps({'username': username, 'password': password})
        ).get('Payload').read()

        return json.loads(response)
    
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Error during confirmation',
                'error': str(e)
            })
        }
