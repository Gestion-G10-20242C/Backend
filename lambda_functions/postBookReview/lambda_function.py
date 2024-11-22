import sys
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

class HTTPError(Exception):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')


def get_user_details(user_id):
    try:
        response = dynamodb_client.get_item(
            TableName='UserProfiles',
            Key={'username': TypeSerializer().serialize(user_id)},
            ProjectionExpression='#nameAlias, profilePicture',
            ExpressionAttributeNames={'#nameAlias': 'name'}
        )
    except Exception as e:
        print(e, file=sys.stderr)
        raise HTTPError(500, 'Failed to query DB')
    try:
        user = response['Item']
    except:
        raise HTTPError(404, 'no user found for that user ID')
    try:
        deser = TypeDeserializer()
        given_name = deser.deserialize(user['name'])
        profile_picture = deser.deserialize(user['profilePicture'])
        return given_name, profile_picture
    except Exception as e:
        print(e, file=sys.stderr)
        raise HTTPError(500, 'error retrieving user details')


def add_review_to_book(book_id, user_id, given_name, profile_picture, user_review):
    # Save new review to DB
    try:
        ser = TypeSerializer()
        response = dynamodb_client.update_item(
            TableName='Books',
            Key={'id': ser.serialize(book_id)},
            UpdateExpression='SET reviews = list_append(if_not_exists(reviews, :empty_list), :new_reviews)',
            ExpressionAttributeValues={
                ':empty_list': ser.serialize([]),
                ':new_reviews': ser.serialize([
                    {
                        "username": user_id,
                        "name": given_name,
                        "profilePicture": profile_picture,
                        "review": user_review,
                    }
                ])
            },
            ReturnValues="ALL_NEW" # devuelve cómo quedó.
        )['Attributes']
    except Exception as e:
        print(e, file=sys.stderr)
        raise HTTPError(500, 'Failed to write changes to DB')
    book = TypeDeserializer().deserialize(response)
    book = {
        'id': book['id'],
        'average_rating': book['average_rating'],
        'publication_date': book['publication_date'],
        'image_url': book['image_url'],
        'author_name': book['author_name'],
        'title': book['title'],
        'genres': book['genres'],
        'reviews': book['reviews']
    }
    return book


def add_review_to_user(book_id, user_id, user_review):
    # Save new review to DB
    try:
        ser = TypeSerializer()
        dynamodb_client.update_item(
            TableName='UserProfiles',
            Key={'username': ser.serialize(user_id)},
            UpdateExpression='SET reviews = list_append(if_not_exists(reviews, :empty_list), :new_reviews)',
            ExpressionAttributeValues={
                ':empty_list': ser.serialize([]),
                ':new_reviews': ser.serialize([
                    {
                        "book_id": book_id,
                        "review:": user_review,    
                    }
                ])
            },
            ReturnValues="NONE"
        )
    except Exception as e:
        print(e, file=sys.stderr)
        raise HTTPError(500, 'Failed to write changes to DB')


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
        user_id = body['user_id']
        user_review = body['user_review']
    except KeyError:
        raise HTTPError(400, 'user_id or user_review body parameter not provided')
    return book_id, user_id, user_review


def lambda_handler(event, _context):
    print(event) # debug
    try:
        book_id, user_id, user_review = parse_input(event)
        given_name, profile_picture = get_user_details(user_id)
        book = add_review_to_book(book_id, user_id, given_name, profile_picture, user_review)
        add_review_to_user(book_id, user_id, user_review)
        response = {
            'statusCode': 200,
            'body': json.dumps(book),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS, POST'
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
                'Access-Control-Allow-Methods': 'OPTIONS, POST'
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
                'Access-Control-Allow-Methods': 'OPTIONS, POST'
            }
        }
