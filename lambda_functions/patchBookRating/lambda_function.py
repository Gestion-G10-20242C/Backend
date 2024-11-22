import sys
import json
import boto3

class HTTPError(Exception):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')


def get_book_rating(book_id):
    try:
        response = dynamodb_client.get_item(
            TableName='Books',
            Key={'id': {'S': book_id}},
            ProjectionExpression='average_rating, ratings_count, ratings_sum'
        )
    except Exception as e:
        print(e, file=sys.stderr)
        raise HTTPError(500, 'Failed to query DB')
    try:
        book = response['Item']
    except:
        raise HTTPError(404, 'no book found for that book_id')
    try:
        average_rating = float(book['average_rating']['N'])
        ratings_count = int(book['ratings_count']['N'])
        ratings_sum = int(book['ratings_sum']['N']) if 'ratings_sum' in book else round(average_rating * ratings_count)
        return ratings_count, ratings_sum
    except Exception as e:
        print(e, file=sys.stderr)
        raise HTTPError(500, 'error retrieving book details')


def rate_book(book_id, user_rating):
    ratings_count, ratings_sum = get_book_rating(book_id)
    ratings_count += 1
    ratings_sum += user_rating
    average_rating = round(ratings_sum / ratings_count, 2)

    # Save new rating to DB
    try:
        response = dynamodb_client.update_item(
            TableName='Books',
            Key={'id': {'S': book_id}},
            UpdateExpression='SET average_rating = :new_avg, ratings_count = :new_count, ratings_sum = :new_sum',
            ExpressionAttributeValues={
                ':new_avg': {'N': str(average_rating)},
                ':new_count': {'N': str(ratings_count)},
                ':new_sum': {'N': str(ratings_sum)}
            },
            ReturnValues="ALL_NEW" # devuelve cómo quedó.
        )['Attributes']
    except Exception as e:
        print(e, file=sys.stderr)
        raise HTTPError(500, 'Failed to write changes to DB')
    book = {
        'id': response['id']['S'],
        'isbn': response['isbn']['S'],
        'average_rating': float(response['average_rating']['N']),
        'publication_date': response['publication_date']['S'],
        'image_url': response['image_url']['S'],
        'author_name': response['author_name']['S'],
        'title': response['title']['S'],
        'genres': response['genres']['S'],
    }
    return book


def parse_input(event):
    try:
        book_id = event['pathParameters']['book_id']
    except KeyError:
        raise HTTPError(400, 'book_id path parameter not provided')
    try:
        body = json.loads(event['body'])
    except Exception as e:
        print(e, file=sys.stderr)
        raise HTTPError(400, 'request body is not valid json')
    try:
        user_rating = body['user_rating']
        if not 1 <= user_rating <= 5:
            raise HTTPError(400, 'Rating must be a number between 1 and 5.')
    except KeyError:
        raise HTTPError(400, 'user_rating body parameter not provided')
    return book_id, user_rating


def lambda_handler(event, _context):
    print(event) # debug
    try:
        book_id, user_rating = parse_input(event)
        book = rate_book(book_id, user_rating)
        response = {
            'statusCode': 200,
            'body': json.dumps(book),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS, PATCH'
            }
        }
        return response
    except HTTPError as e:
        return {
            'statusCode': e.status_code,
            'body': json.dumps({'error_message': e.error_message}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS, PATCH'
            }
        }
    except Exception as e:
        print(e, file=sys.stderr)
        return {
            'statusCode': 500,
            'body': json.dumps({'error_message': 'Unhandled exception'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS, PATCH'
            }
        }

