import json
import boto3
import os
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')

CLIENT_ID = os.environ.get('CLIENT_ID')

def lambda_handler(event, context):
    username = event['username']
    confirmation_code = event['confirmation_code']
    
    try:
        cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            ConfirmationCode=confirmation_code
        )
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User confirmation successful!'
            })
        }
    
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Error during confirmation',
                'error': str(e)
            })
        }
