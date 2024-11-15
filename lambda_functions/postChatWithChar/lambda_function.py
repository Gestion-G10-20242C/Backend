import http.client
import json
import os
from system_prompt import build_system_message
#import dotenv #local test
#dotenv.load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


def send_request_to_openai(user_message, system_message="", model="gpt-3.5-turbo"):
    """Envía la solicitud a la API de OpenAI y devuelve la respuesta del modelo."""
    conn = http.client.HTTPSConnection("api.openai.com")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
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




def lambda_handler(event, context):
    body = json.loads(event['body'])
    system_message = build_system_message(body)
    user_message = body['message']

    try:
        model_response = send_request_to_openai(user_message, system_message)
        return {
            "statusCode": 200,
            "body": model_response
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }


# event = {
#     "body": '{"message": "¿Cuál es la capital de Francia?","role": "foo"}'
# }

# event = {
#     "body":'{"message": "Odio a Harry Potter y vos?","role": "author","name": "J.K. Rowling"}'
# }

# event = {
#     "body":'{"message": "¿Cuál es tu libro favorito?","role": "char","name": "Hermione Granger","book_name": "Harry Potter y la piedra filosofal"}'
# }

