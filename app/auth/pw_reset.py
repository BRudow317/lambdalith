# password_reset_request_lambda.py
import json
import secrets
from datetime import datetime, timedelta

import boto3

def _get_tables():
    dynamodb = boto3.resource("dynamodb")
    return (
        dynamodb.Table("Users"),
        dynamodb.Table("PasswordResetTokens"),
    )


def _get_ses():
    return boto3.client("ses")

API_KEYS = {
    'site_a_key_abc123': {'client_id': 'ClientCustomerC', 'site_id': 'SiteA'},
    'site_b_key_xyz789': {'client_id': 'ClientCustomerA', 'site_id': 'SiteB'}
}

def pw_reset(event):
    """Generate password reset token and send email."""
    try:
        # Validate API key
        api_key = event['headers'].get('x-api-key', '')
        if api_key not in API_KEYS:
            return response(403, {'error': 'Invalid API key'})
        
        tenant = API_KEYS[api_key]
        
        # Parse request
        body = json.loads(event['body'])
        email = body.get('email', '').lower().strip()
        
        if not email:
            return response(400, {'error': 'Email required'})
        
        users_table, reset_tokens_table = _get_tables()
        ses = _get_ses()

        # Lookup user
        user_id = f"{tenant['client_id']}#{tenant['site_id']}#{email}"
        
        try:
            user_response = users_table.get_item(Key={'user_id': user_id})
        except:
            # Don't reveal if user exists
            return response(200, {'message': 'If account exists, reset email sent'})
        
        if 'Item' not in user_response:
            # Don't reveal if user exists
            return response(200, {'message': 'If account exists, reset email sent'})
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(hours=1)
        
        # Store reset token
        reset_tokens_table.put_item(Item={
            'reset_token': reset_token,
            'user_id': user_id,
            'expires_at': expiry.isoformat(),
            'used': False
        })
        
        # Send email (simplified - add proper template)
        reset_link = f"https://{tenant['site_id'].lower()}.com/reset-password?token={reset_token}"
        
        ses.send_email(
            Source='noreply@yourservice.com',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Password Reset Request'},
                'Body': {
                    'Text': {'Data': f'Click here to reset: {reset_link}'}
                }
            }
        )
        
        return response(200, {'message': 'If account exists, reset email sent'})
        
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
