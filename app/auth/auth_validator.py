# auth_validator.py
import json
import os

import boto3
import jwt

CACHED_SECRET = None

def get_secret():
    global CACHED_SECRET
    if CACHED_SECRET:
        return CACHED_SECRET
    
    secret_name = os.environ.get('JWT_SECRET_NAME')
    if not secret_name:
        raise RuntimeError("JWT_SECRET_NAME is not configured")
    secrets_client = boto3.client("secretsmanager")
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret_dict = json.loads(response['SecretString'])
    CACHED_SECRET = secret_dict['jwt_secret']
    return CACHED_SECRET

def auth_validator(event):
    """Validate JWT from headers and return (user_data, error_response)."""
    try:
        auth_header = event['headers'].get('authorization', '')
        if not auth_header.startswith('Bearer '):
            return None, {'statusCode': 401, 'body': json.dumps({'error': 'No token'})}
        
        token = auth_header.split(' ')[1]
        secret = get_secret()
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        
        # Check blacklist
        if 'jti' in payload:
            blacklist_table = os.environ.get('BLACKLIST_TABLE')
            if blacklist_table:
                dynamodb = boto3.resource("dynamodb")
                table = dynamodb.Table(blacklist_table)
                result = table.get_item(Key={'token_jti': payload['jti']})
                if 'Item' in result:
                    return None, {'statusCode': 401, 'body': json.dumps({'error': 'Token revoked'})}
        
        return payload, None
        
    except jwt.ExpiredSignatureError:
        return None, {'statusCode': 401, 'body': json.dumps({'error': 'Token expired'})}
    except jwt.InvalidTokenError:
        return None, {'statusCode': 401, 'body': json.dumps({'error': 'Invalid token'})}
