# lambda_logout.py
import json
import os
from datetime import datetime

import boto3
import jwt

_jwt_secret = None

def _get_jwt_secret():
    global _jwt_secret
    if _jwt_secret is None:
        secret_name = os.environ.get("JWT_SECRET_NAME")
        if not secret_name:
            raise RuntimeError("JWT_SECRET_NAME is not configured")
        secretsmanager = boto3.client("secretsmanager")
        secret_response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret = json.loads(secret_response['SecretString'])
        _jwt_secret = secret['jwt_secret']
    return _jwt_secret


def _get_blacklist_table():
    table_name = os.environ.get("BLACKLIST_TABLE")
    if not table_name:
        raise RuntimeError("BLACKLIST_TABLE is not configured")
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(table_name)


def logout(event):
    try:
        blacklist_table = _get_blacklist_table()
        auth_header = event.get('headers', {}).get('authorization', '')
        if not auth_header.startswith('Bearer '):
            return response(401, {'error': 'No token provided'})
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=['HS256'])
        
        # Add token to blacklist with TTL matching token expiration
        token_jti = payload.get('jti', token[:16])  # Use partial token if no JTI
        exp_timestamp = payload['exp']
        
        blacklist_table.put_item(Item={
            'token_jti': token_jti,
            'ttl': exp_timestamp,
            'blacklisted_at': datetime.utcnow().isoformat()
        })
        
        return response(200, {'message': 'Logged out successfully'})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error'})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }
