import json

def lambda_handler(event, context):
    print(event) #
    # holaaa :)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
