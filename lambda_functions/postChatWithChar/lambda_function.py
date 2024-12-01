import http.client
import json
import os
import boto3
from datetime import datetime
from system_prompt import build_system_message

MAX_MESSAGES = 8
MILIS = 1000

# DynamoDB setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
chats_table = dynamodb.Table('Chats')

API_KEY = os.getenv("OPENAI_API_KEY")

def send_request_to_openai(messages, model="gpt-3.5-turbo"):
    """Envía la solicitud a la API de OpenAI y devuelve la respuesta del modelo."""
    conn = http.client.HTTPSConnection("api.openai.com")
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "n": 1
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    response = json.loads(data)
    return response['choices'][0]['message']['content']

def clean_dynamodb_item(dynamodb_item):
    """Transform DynamoDB item format to standard JSON."""
    return {key: list(value.values())[0] for key, value in dynamodb_item.items()}

def get_chat_history(username, chat_id):
    """Carga el historial del chat desde DynamoDB."""
    response = chats_table.get_item(Key={"username": username, "id": chat_id})  # Usa strings directamente
    history = response.get("Item", {}).get("history", [])
    return history

def save_chat_history(user_id, chat_id, history):
    chats_table.put_item(
        Item={
            "username": user_id,
            "id": chat_id,
            "history": history[-MAX_MESSAGES:]
        }
    )

def lambda_handler(event, context):
    pathParameters = event.get('pathParameters', {})
    body = json.loads(event['body'])
    user_id = pathParameters.get('username')
    chat_id = pathParameters.get('chat_id')
    user_message = body['message']

    # try:
    if chat_id:
        history = get_chat_history(user_id, chat_id)
        messages = history + [{"role": "user", "content": user_message}]
    else:
        chat_id = f"{datetime.now().timestamp()*MILIS:.0f}"
        messages = [{"role": "system", "content": build_system_message(body)},
                    {"role": "user", "content": user_message}]

    model_response = send_request_to_openai(messages)
    messages.append({"role": "assistant", "content": model_response})

    save_chat_history(user_id, chat_id, messages)

    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS, POST'
        },
        "body": json.dumps({
            "chat_id": chat_id,
            "response": model_response
        })
    }
    # except Exception as e:
    #     return {
    #         "statusCode": 500,
    #         "body": f"Error: {str(e)}"
    #     }


event = {
    "body":'{"message": "Cuál es el personaje que más lo ama?","role": "author","name": "J.K. Rowling"}',
    'pathParameters': {
        'username': 'gabitest',
        'chat_id': '1733011669194'
    }
}

# event = {
#     "body":'{"message": "¿Cuál es tu libro favorito?","role": "char","name": "Hermione Granger","book_name": "Harry Potter y la piedra filosofal"}'
# }


print(lambda_handler(event, None))
