import json
import boto3
import os
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')

CLIENT_ID = os.environ.get('CLIENT_ID')

def lambda_handler(event, context):
    username = event['username']
    password = event['password']
    email = event['email']
    
    try:
        response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
            ],
        )
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User signup successful!',
                'userSub': response['UserSub']
            })
        }
    
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Error during signup',
                'error': str(e)
            })
        }
