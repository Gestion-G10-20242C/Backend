import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('UserProfiles')

def lambda_handler(event, context):
    try:
        response = table.scan(ProjectionExpression="username, profilePicture")
        data = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'body': {'users': data, 'lastEvaluatedKey': response.get('LastEvaluatedKey', None)}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
    