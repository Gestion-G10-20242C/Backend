import json
import boto3
import os
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')

CLIENT_ID = os.environ.get('CLIENT_ID')
USER_POOL_ID = os.environ.get('USER_POOL_ID')  

"""
    Handles user signup via AWS Cognito.
    This function checks if the provided email already exists in the Cognito User Pool.
    If the email exists, it returns an error response. If the email does not exist, it
    attempts to sign up the user with the provided username, password, and email.
    Parameters:
    event (dict): A dictionary containing the following keys:
        - username (str): The username for the new user.
        - password (str): The password for the new user.
        - email (str): The email address for the new user.
    Returns:
    dict: A dictionary containing the status code and body. The body is a JSON string with a message
          and, in case of success, the userSub. In case of error, it contains an error message and error type.
"""
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
