"""
register_user.py
User registration Lambda function for multi-tenant application.
Validates API key, registers user in DynamoDB with hashed password.
"""
import json
import bcrypt
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

# API key to tenant mapping
# ToDo: Move to Secrets Manager or secure storage
API_KEYS = {
    'site_a_key_abc123': {'client_id': 'ClientCustomerC', 'site_id': 'SiteA'},
    'site_b_key_xyz789': {'client_id': 'ClientCustomerA', 'site_id': 'SiteB'}
}


def register_user():
    """Register a new user"""
    try:
        # Validate API key
        api_key = event['headers'].get('x-api-key', '')
        if api_key not in API_KEYS:
            return response(403, {'error': 'Invalid API key'})
        
        tenant = API_KEYS[api_key]
        
        # Parse request
        body = json.loads(event['body'])
        email = body.get('email', '').lower().strip()
        password = body.get('password', '')
        name = body.get('name', '')
        
        # Validation
        if not email or not password:
            return response(400, {'error': 'Email and password required'})
        
        if len(password) < 8:
            return response(400, {'error': 'Password must be at least 8 characters'})
        
        # Check if user already exists for this tenant
        user_id = f"{tenant['client_id']}#{tenant['site_id']}#{email}"
        
        try:
            existing = users_table.get_item(Key={'user_id': user_id})
            if 'Item' in existing:
                return response(409, {'error': 'User already exists'})
        except:
            pass
        
        # Hash password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Create user
        users_table.put_item(Item={
            'user_id': user_id,
            'email': email,
            'password_hash': password_hash.decode('utf-8'),
            'name': name,
            'client_id': tenant['client_id'],
            'site_id': tenant['site_id'],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        return response(201, {
            'message': 'Registration successful',
            'user': {
                'user_id': user_id,
                'email': email,
                'name': name
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