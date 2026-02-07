# Users table
{
    'TableName': 'Users',
    'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
    'AttributeDefinitions': [{'AttributeName': 'user_id', 'AttributeType': 'S'}],
    'GlobalSecondaryIndexes': [{
        'IndexName': 'email-index',
        'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}]
    }]
}

# Password reset tokens
{
    'TableName': 'PasswordResetTokens',
    'KeySchema': [{'AttributeName': 'reset_token', 'KeyType': 'HASH'}],
    'TimeToLiveSpecification': {
        'Enabled': True,
        'AttributeName': 'ttl'  # Auto-delete expired tokens
    }
}

# Token blacklist (for logout)
{
    'TableName': 'TokenBlacklist',
    'KeySchema': [{'AttributeName': 'token_jti', 'KeyType': 'HASH'}],
    'TimeToLiveSpecification': {
        'Enabled': True,
        'AttributeName': 'ttl'
    }
}

# Login attempts (rate limiting)
{
    'TableName': 'LoginAttempts',
    'KeySchema': [{'AttributeName': 'identifier', 'KeyType': 'HASH'}],  # email or IP
    'TimeToLiveSpecification': {
        'Enabled': True,
        'AttributeName': 'ttl'
    }
}