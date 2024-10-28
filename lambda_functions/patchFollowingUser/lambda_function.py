import json
import boto3

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):

    username = event['username']
    user_following = event['following']
    active = event['active']

    response = dynamodb_client.update_item(
        TableName='Follows',
        Key={'username': {'S': username}, 'following': {'S': user_following}},
        UpdateExpression="SET active = :active",
        ExpressionAttributeValues={
            ':active': {'BOOL': active}
        },
        ReturnValues="UPDATED_NEW"
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }


    return {
        'statusCode': 200,
        'body': json.dumps(response['Attributes'])
    }
