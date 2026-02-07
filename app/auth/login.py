"""
lambda_login.py
User login Lambda function for multi-tenant application.
Validates credentials and returns JWT.
"""
import json
import os
from datetime import datetime, timedelta

import bcrypt
import boto3
import jwt
JWT_EXPIRY_HOURS = 24

API_KEYS = {
    'site_a_key_abc123': {'client_id': 'ClientCustomerC', 'site_id': 'SiteA'},
    'site_b_key_xyz789': {'client_id': 'ClientCustomerA', 'site_id': 'SiteB'}
}

def _get_users_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table("Users")


def _get_jwt_secret():
    jwt_secret = os.environ.get("JWT_SECRET")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET is not configured")
    return jwt_secret


def login(event):
    """Authenticate user and return JWT."""
    try:
        users_table = _get_users_table()
        api_key = event['headers'].get('x-api-key', '')
        if api_key not in API_KEYS:
            return response(403, {'error': 'Invalid API key'})
        
        tenant = API_KEYS[api_key]
        
        
        body = json.loads(event['body'])
        email = body.get('email', '').lower().strip()
        password = body.get('password', '')
        
        if not email or not password:
            return response(400, {'error': 'Email and password required'})
        
        
        user_id = f"{tenant['client_id']}#{tenant['site_id']}#{email}"
        
        try:
            user_response = users_table.get_item(Key={'user_id': user_id})
        except Exception as e:
            print(f"DB Error: {str(e)}")
            return response(500, {'error': 'Database error'})
        
        if 'Item' not in user_response:
            return response(401, {'error': 'Invalid credentials'})
        
        user = user_response['Item']
        
        
        stored_hash = user['password_hash'].encode('utf-8')
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return response(401, {'error': 'Invalid credentials'})
        
        
        payload = {
            'user_id': user['user_id'],
            'email': user['email'],
            'client_id': tenant['client_id'],
            'site_id': tenant['site_id'],
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, _get_jwt_secret(), algorithm='HS256')
        
        # Update last login
        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET last_login = :login_time',
            ExpressionAttributeValues={':login_time': datetime.utcnow().isoformat()}
        )
        
        return response(200, {
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'email': user['email'],
                'name': user.get('name', '')
            }
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
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
