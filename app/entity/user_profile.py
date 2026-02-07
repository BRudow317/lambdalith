# src/user_profile/user_profile_lambda.py
import json
import jwt
import os
import boto3

JWT_SECRET_NAME = os.environ['JWT_SECRET_NAME']
BLACKLIST_TABLE = os.environ['BLACKLIST_TABLE']

secretsmanager = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')
blacklist_table = dynamodb.Table(BLACKLIST_TABLE)

# Cache the secret
_jwt_secret = None

def get_jwt_secret():
    global _jwt_secret
    if _jwt_secret is None:
        secret_response = secretsmanager.get_secret_value(SecretId=JWT_SECRET_NAME)
        secret = json.loads(secret_response['SecretString'])
        _jwt_secret = secret['jwt_secret']
    return _jwt_secret

def user_profile():
    try:
        # Get token from Authorization header
        auth_header = event.get('headers', {}).get('authorization', '')
        if not auth_header.startswith('Bearer '):
            return response(401, {'error': 'No token provided'})
        
        token = auth_header.split(' ')[1]
        
        # Verify JWT
        payload = jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])
        
        # Check if token is blacklisted
        token_jti = payload.get('jti')  # You'll need to add this to token generation
        if token_jti:
            try:
                blacklist_response = blacklist_table.get_item(Key={'token_jti': token_jti})
                if 'Item' in blacklist_response:
                    return response(401, {'error': 'Token has been revoked'})
            except:
                pass
        
        # Return user profile
        return response(200, {
            'user': {
                'user_id': payload['user_id'],
                'email': payload['email'],
                'client_id': payload['client_id'],
                'site_id': payload['site_id']
            }
        })
        
    except jwt.ExpiredSignatureError:
        return response(401, {'error': 'Token expired'})
    except jwt.InvalidTokenError:
        return response(401, {'error': 'Invalid token'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error'})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }