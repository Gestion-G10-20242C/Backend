from decimal import Decimal
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

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


def addCORSHeader(response):
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS, GET'
    }
    return response

"""
Lambda function to retrieve a user profile from a DynamoDB table.
Parameters:
event (dict): The event dictionary containing request parameters.
    - pathParameters (dict): Dictionary containing path parameters.
        - username (str): The username of the user profile to retrieve.
Returns:
dict: A dictionary containing the HTTP status code and the response body.
    - statusCode (int): The HTTP status code of the response.
    - body (str): The JSON-encoded response body.
        - On success: JSON-encoded user profile.
        - On failure: JSON-encoded error message.
"""
def lambda_handler(event, context):
    id = event['pathParameters']['book_id']
    print(id)
    
    response = dynamodb_client.get_item(
        TableName='Books',
        Key={
            'id': {
                'S': id
            }
        }
    )
    
    # Verificación del estado de la respuesta
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }
    
    if 'Item' not in response:
        return addCORSHeader({
            'statusCode': 404,
            'body': json.dumps('Error: Perfil no encontrado')
        })
    
    deserializer = TypeDeserializer()
    
    return addCORSHeader({
        'statusCode': 200,
        'body': json.dumps(clean_dynamodb_item(response['Item']), cls=DecimalEncoder)
    })


# event = {
#     'pathParameters': {
#         'book_id': 'e31ad55b-01b3-4cc1-813f-f7d978694ab1'
#     }
# }

# print(lambda_handler(event, None))