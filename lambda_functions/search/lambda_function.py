import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

# aux, hardcoded response for formatting testing
#aux_response = {'Items': [{'average_rating': {'N': '3.85'}, 'publication_date': {'S': '2005-6-30'}, 'text_reviews_count': {'N': '1280'}, 'image_url': {'S': 'https://images.gr-assets.com/books/1375746052m/182381.jpg'}, 'author_name': {'S': 'Elizabeth Gaskell'}, 'title': {'S': 'Cranford'}}], 'Count': 1, 'ScannedCount': 1, 'ResponseMetadata': {'RequestId': '7Q4EFLIDL2AHS20PPB2EGQN96JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Sun, 03 Nov 2024 09:39:04 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '284', 'connection': 'keep-alive', 'x-amzn-requestid': '7Q4EFLIDL2AHS20PPB2EGQN96JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3468948407'}, 'RetryAttempts': 0}}

def deserialize_items(items):
    return [
        {
            'average_rating': float(item['average_rating']['N']),
            'publication_date': item['publication_date']['S'],
            'text_reviews_count': int(item['text_reviews_count']['N']),
            'image_url': item['image_url']['S'],
            'author_name': item['author_name']['S'],
            'title': item['title']['S'],
            'genres': item['genres']['S'],
        }
        for item in items
    ]

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
    
    books = deserialize_items(response['Items'])
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
    ProjectionExpression="image_url, title, author_name, genres, average_rating, text_reviews_count, publication_date"
    )
    print(response)
    
    return response


def lambda_handler(event, context):
    print(event) # debug
    query = event.get('queryStringParameters', {}).get('query', None) # aux
    field = event.get('queryStringParameters', {}).get('field', None)

    case_insentive_query = query.title()
    response = search_books_by(field, case_insentive_query)

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
    
    books = deserialize_items(response['Items'])
    
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
#event = {}
#print("Books:", lambda_handler(event, {}))