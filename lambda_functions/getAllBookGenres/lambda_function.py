import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('BookGenres')

def lambda_handler(event, context):
    try:
        response = table.scan()
        data = response.get('Items', [])    
        deserialedData = [{'genre': item.get('name'), 'count': int(item.get('count', 0))} for item in data]

        return {
            'statusCode': 200,
            'body': {'genres': deserialedData}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }