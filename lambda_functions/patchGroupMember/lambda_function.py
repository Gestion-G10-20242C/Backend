import json
import boto3

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    username = event['pathParameters']['username']
    group_id = event['pathParameters']['group_id']
    active = json.loads(event['body']).get('active')
    
    if active is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }

    response = dynamodb_client.update_item(
        TableName='Members',
        Key={'id': {'N': group_id}, 'username': {'S': username}},
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
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, PATCH'
        },
        'body': json.dumps(response['Attributes'])
    }

# event = {
#     'pathParameters': {
#         'username': 'gabitest',
#         'group_id': '1731697690123'
#     },
#     'body': '{"active": true}'
# }

# print(lambda_handler(event, None))