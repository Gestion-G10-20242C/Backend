import json
import boto3
import os
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')

CLIENT_ID = os.environ.get('CLIENT_ID', '2i7rhsvoo43nqblk2h8ucrfa8v')
USER_POOL_ID = os.environ.get('USER_POOL_ID', 'us-east-1_1r6FDZzId')  

def lambda_handler(event, context):
    username = event['username']
    password = event['password']
    email = event['email']

    try:
        existing_users = cognito_client.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'email="{email}"'
        )
        
        if existing_users['Users']:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Email already exists',
                    'error': 'EmailAlreadyExists'
                })
            }
    
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Error checking if email exists',
                'error': str(e)
            })
        }
    

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
