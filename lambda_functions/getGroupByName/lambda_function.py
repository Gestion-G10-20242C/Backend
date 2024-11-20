import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    group_id = event['pathParameters']['group_id']

    try:
        print(f"Searching for group with ID {group_id}")
        response = dynamodb_client.get_item(
            TableName='Groups',
            Key={'id': {'N': group_id}}
        )
        print(f"Found {len(response.get('Items', []))} groups with matching ID")

        response = dynamodb_client.scan(
            TableName='Groups',
            FilterExpression="contains(#name, :query)",
            ExpressionAttributeNames={
                '#name': 'name' 
            },
            ExpressionAttributeValues={
                ':query': {'S': group_id}
            }
        )
        print(f"Found {len(response.get('Items', []))} groups with matching name")

        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            return {
                'statusCode': 400,
                'body': json.dumps('Error while querying DynamoDB')
            }

        # Obtener y deserializar los elementos
        items = response.get('Items', [])
        deserializer = TypeDeserializer()
        items = [{k: deserializer.deserialize(v) for k, v in item.items()} for item in items]

        # Responder con los datos obtenidos
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS, GET'
            },
            'body': json.dumps(items)
        }

    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error')
        }

# event = {
#     'pathParameters': {'group_id': '1731699934304'},
#     'body': '{"description": "El mejor libro del mundo", "image_url":"https://i.pinimg.com/736x/f8/77/11/f8771136acc302740ba301d51d39cf7a.jpg", "genres": "Gabigol"}'
# }
# lambda_handler(event, None)