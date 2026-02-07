# Function URL event structure
def url_events():
    # Headers
    headers = event.get('headers', {})
    api_key = headers.get('x-api-key', '')
    
    # already parsed for you
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body)
    
    # HTTP method
    method = event.get('requestContext', {}).get('http', {}).get('method', '')
    
    # Return format
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            # CORS handled by FunctionUrlConfig
        },
        'body': json.dumps({'message': 'success'})
    }