# lambda_pw_reset_confirm.py
import json
from datetime import datetime

import bcrypt
import boto3

def _get_tables():
    dynamodb = boto3.resource("dynamodb")
    return (
        dynamodb.Table("Users"),
        dynamodb.Table("PasswordResetTokens"),
    )

def pw_reset_confirm(event):
    """Reset password using valid token."""
    try:
        users_table, reset_tokens_table = _get_tables()

        body = json.loads(event['body'])
        reset_token = body.get('token', '')
        new_password = body.get('new_password', '')
        
        if not reset_token or not new_password:
            return response(400, {'error': 'Token and new password required'})
        
        if len(new_password) < 8:
            return response(400, {'error': 'Password must be at least 8 characters'})
        
        # Validate token
        try:
            token_response = reset_tokens_table.get_item(Key={'reset_token': reset_token})
        except:
            return response(400, {'error': 'Invalid or expired token'})
        
        if 'Item' not in token_response:
            return response(400, {'error': 'Invalid or expired token'})
        
        token_data = token_response['Item']
        
        # Check if used
        if token_data.get('used', False):
            return response(400, {'error': 'Token already used'})
        
        # Check expiry
        expiry = datetime.fromisoformat(token_data['expires_at'])
        if datetime.utcnow() > expiry:
            return response(400, {'error': 'Token expired'})
        
        # Hash new password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        
        # Update user password
        users_table.update_item(
            Key={'user_id': token_data['user_id']},
            UpdateExpression='SET password_hash = :hash, updated_at = :updated',
            ExpressionAttributeValues={
                ':hash': password_hash.decode('utf-8'),
                ':updated': datetime.utcnow().isoformat()
            }
        )
        
        # Mark token as used
        reset_tokens_table.update_item(
            Key={'reset_token': reset_token},
            UpdateExpression='SET used = :used',
            ExpressionAttributeValues={':used': True}
        )
        
        return response(200, {'message': 'Password reset successful'})
        
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
