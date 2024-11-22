import sys
import json
import boto3

class HTTPError(Exception):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')


def get_user_details(user_id):
    try:
        response = dynamodb_client.get_item(
            TableName='UserProfiles',
            Key={'username': {'S': user_id}},
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
        given_name = user['name']['S']
        profile_picture = user['profilePicture']['S']
        return given_name, profile_picture
    except Exception as e:
        print(e, file=sys.stderr)
        raise HTTPError(500, 'error retrieving user details')


def add_review_to_book(book_id, user_id, given_name, profile_picture, user_review):
    # Save new review to DB
    try:
        response = dynamodb_client.update_item(
            TableName='Books',
            Key={'id': {'S': book_id}},
            UpdateExpression='ADD reviews :new_reviews',
            ExpressionAttributeValues={
                ':new_reviews': { 'L': [{
                    "M": {
                        "user_id": {"S": user_id},
                        "user_name:": {"S": given_name},
                        "profilePicture:": {"S": profile_picture},
                        "review:": {"S": user_review},    
                    }
                }]}
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
        'text_reviews_count': int(response['text_reviews_count']['N']),
        'image_url': response['image_url']['S'],
        'author_name': response['author_name']['S'],
        'title': response['title']['S'],
        'genres': response['genres']['S'],
        'reviews': [
            {
                'username': review['M']['user_id']['S'],
                'name': review['M']['user_name']['S'],
                'profilePicture': review['M']['profilePicture']['S'],
                'review': review['M']['review']['S']
            }
            for review in response['reviews']['L']
        ],
    }
    return book


def add_review_to_user(book_id, user_id, user_review):
    # Save new review to DB
    try:
        dynamodb_client.update_item(
            TableName='UserProfiles',
            Key={'username': {'S': user_id}},
            UpdateExpression='ADD reviews :new_reviews',
            ExpressionAttributeValues={
                ':new_reviews': { 'L': [{
                    "M": {
                        "book_id": {"S": book_id},
                        "review:": {"S": user_review},    
                    }
                }]}
            },
            ReturnValues="NONE"
        )['Attributes']
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
