import json
import boto3
import os
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')

CLIENT_ID = os.environ.get('CLIENT_ID')

def lambda_handler(event, context):
    username = event['username']
    password = event['password']
    
    try:
        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            },
            ClientId=CLIENT_ID
        )
        
        access_token = response['AuthenticationResult']['AccessToken']
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Authentication successful!',
                'username':username,
                'access_token': access_token
            })
        }
    
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Error during authentication',
                'error': str(e)
            })
        }
