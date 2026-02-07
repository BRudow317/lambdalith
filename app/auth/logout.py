# lambda_logout.py
import json
import jwt
import os
import boto3
from datetime import datetime

JWT_SECRET_NAME = os.environ['JWT_SECRET_NAME']
BLACKLIST_TABLE = os.environ['BLACKLIST_TABLE']

secretsmanager = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')
blacklist_table = dynamodb.Table(BLACKLIST_TABLE)

_jwt_secret = None

def get_jwt_secret():
    global _jwt_secret
    if _jwt_secret is None:
        secret_response = secretsmanager.get_secret_value(SecretId=JWT_SECRET_NAME)
        secret = json.loads(secret_response['SecretString'])
        _jwt_secret = secret['jwt_secret']
    return _jwt_secret

def logout():
    try:
        auth_header = event.get('headers', {}).get('authorization', '')
        if not auth_header.startswith('Bearer '):
            return response(401, {'error': 'No token provided'})
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])
        
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