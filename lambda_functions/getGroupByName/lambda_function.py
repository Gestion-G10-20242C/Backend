import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal
import urllib.parse


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


def get_users_by_group(group_id):
    """Get the active members of a group by group_id."""
    # Step 1: Filtrar los miembros del grupo
    response = dynamodb_client.scan(
        TableName='Members',
        FilterExpression='id = :id AND active = :active',
        ExpressionAttributeValues={
            ':id': {'N': str(group_id)},
            ':active': {'BOOL': True}
        },
        ProjectionExpression='username'
    )

    # Step 2: Obtener detalles de los perfiles de usuario
    keys = response.get('Items', [])
    if not keys:
        return []

    response = dynamodb_client.batch_get_item(
        RequestItems={
            'UserProfiles': {
                'Keys': keys,
                'ProjectionExpression': 'username, profilePicture, active'
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
    print(event.get('pathParameters', {}))
    group_id = urllib.parse.unquote(event['pathParameters']['group_id'])


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



# event = {'resource': '/groups/{group_id}', 'path': '/groups/snoopy', 'httpMethod': 'GET', 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'no-cache', 'Host': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'Postman-Token': '764f01e2-028b-488e-a077-a2fc88444b7b', 'User-Agent': 'PostmanRuntime/7.42.0', 'X-Amzn-Trace-Id': 'Root=1-673e2055-713dc56059100bd32e75d4ab', 'X-Forwarded-For': '201.231.14.246', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'], 'Cache-Control': ['no-cache'], 'Host': ['nev9ddp141.execute-api.us-east-1.amazonaws.com'], 'Postman-Token': ['764f01e2-028b-488e-a077-a2fc88444b7b'], 'User-Agent': ['PostmanRuntime/7.42.0'], 'X-Amzn-Trace-Id': ['Root=1-673e2055-713dc56059100bd32e75d4ab'], 'X-Forwarded-For': ['201.231.14.246'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': {'group_id': 'snoopy'}, 'stageVariables': None, 'requestContext': {'resourceId': 'rx9rwa', 'resourcePath': '/groups/{group_id}', 'httpMethod': 'GET', 'extendedRequestId': 'Bjn9XFoOIAMEIIg=', 'requestTime': '20/Nov/2024:17:45:57 +0000', 'path': '/prod/groups/Agile%20Beasts', 'accountId': '349609960822', 'protocol': 'HTTP/1.1', 'stage': 'prod', 'domainPrefix': 'nev9ddp141', 'requestTimeEpoch': 1732124757104, 'requestId': 'fd45bbf3-1944-4c18-9e2b-18548f9ab9aa', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '201.231.14.246', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'PostmanRuntime/7.42.0', 'user': None}, 'domainName': 'nev9ddp141.execute-api.us-east-1.amazonaws.com', 'deploymentId': 'bzcxkx', 'apiId': 'nev9ddp141'}, 'body': None, 'isBase64Encoded': False}
# print(lambda_handler(event, None))