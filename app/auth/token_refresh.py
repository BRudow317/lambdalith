# refresh_token_lambda.py
import json
import jwt
import os
import boto3
from datetime import datetime, timedelta, timezone

# Initialize Boto3 client outside handler (reuse connection)
secrets_client = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')

# Env vars from template
SECRET_NAME = os.environ.get('JWT_SECRET_NAME')
USERS_TABLE_NAME = os.environ.get('USERS_TABLE')
JWT_EXPIRY_HOURS = 24
REFRESH_THRESHOLD_HOURS = 2 

# Cache the secret in global scope to reduce API calls
CACHED_SECRET = None

def get_secret():
    global CACHED_SECRET
    if CACHED_SECRET:
        return CACHED_SECRET
    
    try:
        response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
        # Parse the JSON string stored in Secrets Manager
        secret_dict = json.loads(response['SecretString'])
        CACHED_SECRET = secret_dict['jwt_secret']
        return CACHED_SECRET
    except Exception as e:
        print(f"Failed to fetch secret: {e}")
        raise e

def token_refresh():
    try:
        # 1. Handle Case-Insensitive Headers
        headers = {k.lower(): v for k, v in event.get('headers', {}).items()}
        auth_header = headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return response(401, {'error': 'No token provided'})
        
        token = auth_header.split(' ')[1]
        signing_key = get_secret()
        
        # 2. Decode (Verify signature, ignore expiration for now)
        try:
            payload = jwt.decode(
                token, 
                signing_key, 
                algorithms=['HS256'],
                options={"verify_exp": False}
            )
        except jwt.InvalidSignatureError:
             return response(401, {'error': 'Invalid token signature'})

        # 3. Check Expiration Logic (Python 3.14 compatible)
        exp_timestamp = payload['exp']
        # Usage of timezone.utc is required for newer Python
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_left = exp_datetime - now
        
        if time_left.total_seconds() < 0:
            return response(401, {'error': 'Token expired. Please log in again.'})
        
        if time_left.total_seconds() > (REFRESH_THRESHOLD_HOURS * 3600):
            return response(400, {'error': 'Token still valid, refresh not needed'})

        # 4. SECURITY CHECK: Verify User is still active in DB
        table = dynamodb.Table(USERS_TABLE_NAME)
        user_record = table.get_item(Key={'user_id': payload['user_id']})
        
        if 'Item' not in user_record:
            return response(403, {'error': 'User no longer exists'})
            
        # Optional: Check if user is 'banned' or 'active' field here
        # if user_record['Item'].get('status') == 'banned': ...

        # 5. Issue New Token
        new_payload = {
            'user_id': payload['user_id'],
            'email': payload['email'],
            # ... copy other necessary claims ...
            'exp': now + timedelta(hours=JWT_EXPIRY_HOURS),
            'iat': now
        }
        
        new_token = jwt.encode(new_payload, signing_key, algorithm='HS256')
        
        return response(200, {'token': new_token})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # In prod, be careful not to return raw error details to client
        return response(500, {'error': 'Internal server error'})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }