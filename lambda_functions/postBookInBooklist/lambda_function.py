import ast
from boto3.dynamodb.conditions import Attr
import boto3
import json

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

def clean_dynamodb_item(dynamodb_item):
    """Transform DynamoDB item format to standard JSON."""
    return [list(value.values())[0] for key, value in dynamodb_item.items()]

def add_cors_headers(response):
    """Add CORS headers to response."""
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS, POST'
    }

    return response


def lambda_handler(event, context):
    username = event['pathParameters']['username']
    booklist_name = event['pathParameters']['booklist']
    body = json.loads(event['body'])

    # Obtener el item de DynamoDB
    item = get_booklist(username, booklist_name)
    if not item:
        return add_cors_headers({
            'statusCode': 404,
            'body': json.dumps('Booklist not found')
        })

    # Validar y actualizar el libro
    books = parse_books(item['books']['S'])
    if any(book == body['id'] for book,_,_ in books):
        return add_cors_headers({
            'statusCode': 400,
            'body': json.dumps('Book is already in booklist')
        })

    books.append(get_book_data(body['id']))

    # Actualizar el item en DynamoDB
    if not update_books(username, booklist_name, json.dumps(books)):
        return add_cors_headers({
            'statusCode': 400,
            'body': json.dumps('Error updating booklist')
        })

    item['books']['S'] = books 
    return add_cors_headers({
        'statusCode': 200,
        'body': item
    })


def get_booklist(username, booklist_name):
    """Obtiene un item de la tabla DynamoDB."""
    response = dynamodb_client.get_item(
        TableName='Booklists',
        Key={
            'username': {'S': username},
            'name': {'S': booklist_name}
        }
    )
    return response.get('Item')


def get_book_data(book_id):
    """Obtiene la image_url de un libro desde la tabla Books."""
    response = dynamodb_client.get_item(
        TableName='Books',
        Key={
            'id': {'S': book_id}
        },
        ProjectionExpression='id,title,image_url'
    )
    return clean_dynamodb_item(response['Item'])


def parse_books(books_str):
    """Convierte el string de libros de DynamoDB en una lista de Python."""
    return ast.literal_eval(books_str)


def update_books(username, booklist_name, books_json):
    """Actualiza el atributo 'books' de un item en DynamoDB."""
    response = dynamodb_client.update_item(
        TableName='Booklists',
        Key={
            'username': {'S': username},
            'name': {'S': booklist_name}
        },
        UpdateExpression='SET books = :books',
        ExpressionAttributeValues={
            ':books': {'S': books_json}
        },
        ReturnConsumedCapacity='TOTAL'
    )
    return response['ResponseMetadata']['HTTPStatusCode'] == 200


# event = {
#     'pathParameters': {'username': 'gabitest', 'booklist': 'Leidos'},
#     'body': '{"id":"622bf611-4355-446d-a102-548642b3cfc3"}'
# }
# print(lambda_handler(event, None))