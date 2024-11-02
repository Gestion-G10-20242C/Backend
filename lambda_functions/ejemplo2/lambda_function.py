import json

def lambda_handler(event, context):
    
    print("Hola?")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda ejemplo2!')
    }