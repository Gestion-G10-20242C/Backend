import json

def lambda_handler(event, context):
    
    print("Holaa :)")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda ejemplo1!')
    }