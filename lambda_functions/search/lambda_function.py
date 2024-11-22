import json
import boto3
import decimal
from boto3.dynamodb.types import TypeDeserializer

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')


# More efficient but exact only search
def exact_search_books_by(field, index, query):
    print("searching book...")
    response = dynamodb_client.query(
        TableName='Books',
        IndexName=index,
        KeyConditionExpression=f"{field} = :query",
        ExpressionAttributeValues={
        ':query': {'S': query}
        },
        ProjectionExpression="id, image_url, title, author_name, average_rating, text_reviews_count, publication_date, reviews"
    )
    
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
    
    books = TypeDeserializer().deserialize({'L': [{'M': item} for item in response['Items']]})
    return books

# Less efficient but parcial search
def search_books_by(field, query):
    if field:
        expression = f"contains({field}, :query)"
    else:
        expression = "contains(title, :query) OR contains(author_name, :query) OR contains(genres, :query)"

    print(f"Query: {query}, field: {field}\nSearching book...")
    response = dynamodb_client.scan(
      TableName='Books',
      FilterExpression=expression,
      ExpressionAttributeValues={
        ':query': {'S': query}
    },
    ProjectionExpression="id, image_url, title, author_name, genres, average_rating, publication_date, reviews"
    )
    return response


def lambda_handler(event, context):
    query = event.get('queryStringParameters', {}).get('query', None) # aux
    field = event.get('queryStringParameters', {}).get('field', None)

    response = search_books_by(field, query)
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
    books = TypeDeserializer().deserialize({'L': [{'M': item} for item in response['Items']]})
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, GET'
        },
        'body': json.dumps(books, cls=DecimalEncoder)
    }
