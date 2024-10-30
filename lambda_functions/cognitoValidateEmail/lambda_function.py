import json
import boto3
import os
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')
lambda_client = boto3.client('lambda')

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
        
        response = cognito_client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )

        lambda_client.invoke(
            FunctionName='postUserProfile',
            InvocationType='Event',
            Payload=json.dumps({'pathParameters': {'username': username}, 'body': '{}'})
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User confirmation and authentication successful!',
                'access_token': response['AuthenticationResult'].get('IdToken', None)
            })
        }
    
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Error during confirmation or authentication',
                'error': str(e)
            })
        }

