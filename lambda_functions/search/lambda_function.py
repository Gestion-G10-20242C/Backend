import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    print(event)
    query = "Cranford" # aux
    #query = event['pathParameters']['query']
    #print(query)
    
    print("searching book...")
    response = dynamodb_client.query(
        TableName='Books',
        IndexName='title-index',
        KeyConditionExpression='title = :query',
        ExpressionAttributeValues={
        ':query': {'S': query}
        },
        ProjectionExpression="image_url, title, author_name, average_rating, text_reviews_count, publication_date"
    )
    print(response)
    
    # Verificación del estado de la respuesta
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': json.dumps('Error')
        }
    
    if 'Items' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps('Error: No books found')
        }
    
    #deserializer = TypeDeserializer()
    #books = {k: deserializer.deserialize(v) for k, v in response['Items'].items()}
    deserializer = TypeDeserializer()
    books = [ {k: deserializer.deserialize(v) for k, v in item.items()} for item in response['Items'] ]

    
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
#print("Books:", lambda_handler(event, {}))