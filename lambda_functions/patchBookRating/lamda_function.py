import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

# aux, hardcoded response for formatting testing
#aux_response = {'Items': [{'average_rating': {'N': '3.85'}, 'publication_date': {'S': '2005-6-30'}, 'text_reviews_count': {'N': '1280'}, 'image_url': {'S': 'https://images.gr-assets.com/books/1375746052m/182381.jpg'}, 'author_name': {'S': 'Elizabeth Gaskell'}, 'title': {'S': 'Cranford'}}], 'Count': 1, 'ScannedCount': 1, 'ResponseMetadata': {'RequestId': '7Q4EFLIDL2AHS20PPB2EGQN96JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Sun, 03 Nov 2024 09:39:04 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '284', 'connection': 'keep-alive', 'x-amzn-requestid': '7Q4EFLIDL2AHS20PPB2EGQN96JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3468948407'}, 'RetryAttempts': 0}}

def deserialize_book(book):
    return{
            'book_id': int(book['id']['N']),
            'average_rating': float(book['average_rating']['N']),
            'ratings_count': int(book['ratings_count']['N']),
    }

def rate_book(book_id, user_rate):
    # Get book_id
    response = dynamodb_client.get_item(
        TableName='Books',
        Key={'id': {'S': book_id}},
        ProjectionExpression='id, average_rating, ratings_count'
    )

    # camino feliz, response dio ok
    book = deserialize_book(response)
    # New avg _ ((avg*count) + user_rate)/ (count+1)
    new_sum = book['average_rating']*book['ratings_count'] + user_rate
    new_rate_count = book['ratings_count'] + 1
    new_avg_rate = new_sum/new_rate_count

    # Update book avg on db
    response = dynamodb_client.update_item(
        TableName='Books',
        Key={'id': {'S': book_id}},
        UpdateExpression='SET average_rating = :new_avg, ratings_count = :new_count',
        ExpressionAttributeValues={
            ':new_avg': {'N': str(new_avg_rate)},
            ':new_count': {'N': str(new_rate_count)}
        },
        ReturnValues="UPDATED_NEW" # devuelve cómo quedó.
    )

    # camino feliz, dio ok    
    print(response)
    
    return response

def review_book(book_id, user_rate):
    ### ToDo.
    # Get book_id
    response = dynamodb_client.get_item(
        TableName='Books',
        Key={'id': {'S': book_id}},
        ProjectionExpression='id, average_rating, ratings_count'
    )

    # camino feliz, response dio ok
    #book = deserialize_book(response)
    # Review
    
    return response



def lambda_handler(event, context):
    print(event) # debug
    book_id = event['pathParameters']['book_id']    
    body = json.loads(event['body'])
    user_rate = body.get('user_rate')
    user_review = body.get('user_review')

    if user_rate:
        print(f"User submits to book rate {user_rate}")
        response = rate_book(book_id, user_rate)

    if user_review:
        print(f"User submits to book review {user_review}")
        response = {} #toDo


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
    
    
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, GET'
        },
        'body': json.dumps(response)
    }

###
# For local testing:
#event = {}
#print("Books:", lambda_handler(event, {}))