import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    query = event['pathParameters']['query']
    print(query)
    
    # Aux, búsqueda exacta por ahora
    response = dynamodb_client.get_item(
        TableName='Books',
        Key={
            'title': {
                'S': query
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
        return {
            'statusCode': 404,
            'body': json.dumps('Error: Book not found')
        }
    
    deserializer = TypeDeserializer()
    books = {k: deserializer.deserialize(v) for k, v in response['Item'].items()}
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, GET'
        },
        'body': json.dumps(books)
    }


###
# For local testing:
#event = 
#print("User:", lambda_handler(event, {}))