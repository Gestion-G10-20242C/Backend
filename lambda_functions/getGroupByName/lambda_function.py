import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)


def clean_dynamodb_item(dynamodb_item):
    """Transform DynamoDB item format to standard JSON."""
    deserializer = TypeDeserializer()
    return {key: deserializer.deserialize(value) for key, value in dynamodb_item.items()}


def deserialize_usernames(dynamodb_items):
    """Deserialize usernames from DynamoDB scan results."""
    return [{'username': item['username']['S']} for item in dynamodb_items]


def get_users_by_group(group_id):
    """Get the members of a group by group_id."""
    response = dynamodb_client.scan(
        TableName='Members',
        FilterExpression='id = :id',
        ExpressionAttributeValues={':id': {'N': str(group_id)}},
        ProjectionExpression='username'
    )

    usernames = deserialize_usernames(response.get('Items', []))
    
    if not usernames:
        return []

    keys = [{'username': {'S': username['username']}} for username in usernames]

    response = dynamodb_client.batch_get_item(
        RequestItems={
            'UserProfiles': {
                'Keys': keys,
                'ProjectionExpression': 'username, profilePicture'
            }
        }
    )
    
    
    user_profiles = response.get('Responses', {}).get('UserProfiles', [])
    deserializer = TypeDeserializer()
    return [
        {key: deserializer.deserialize(value) for key, value in user.items()}
        for user in user_profiles
    ]


def lambda_handler(event, context):
    print(event)
    group_id = event['pathParameters']['group_id']

    try:
        # Determine if group_id is numeric
        is_numeric = group_id.isdigit()

        # Query the Groups table
        if is_numeric:
            response = dynamodb_client.scan(
                TableName='Groups',
                FilterExpression='id = :id',
                ExpressionAttributeValues={':id': {'N': group_id}}
            )
        else:
            response = dynamodb_client.scan(
                TableName='Groups',
                FilterExpression='contains(#name, :query)',
                ExpressionAttributeNames={'#name': 'name'},
                ExpressionAttributeValues={':query': {'S': group_id}}
            )

        groups = [clean_dynamodb_item(item) for item in response.get('Items', [])]

        if not groups:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Group not found'})
            }

        # Fetch group members and their profiles
        for group in groups:
            group_id = group['id']
            group['members'] = get_users_by_group(group_id)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS, GET'
            },
            'body': json.dumps(groups, cls=DecimalEncoder)  # Usar DecimalEncoder aquí
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'Error': str(e)})
        }



# event = {
#     'pathParameters': {'group_id': '1731699934304'},
#     'body': '{"description": "El mejor libro del mundo", "image_url":"https://i.pinimg.com/736x/f8/77/11/f8771136acc302740ba301d51d39cf7a.jpg", "genres": "Gabigol"}'
# }
# print(lambda_handler(event, None))