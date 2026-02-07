# Cloud Voyages Lambda - Multi-Service Auth Platform

## Links
- [CDK Intro](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)
- [CDK API Reference](https://docs.aws.amazon.com/cdk/api/v2/python/index.html)
- [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli-configure.html)

## Command List
```python
# Initialize a new CDK project
cdk init app --language python
# 
cdk synth
# Deploy the stack to AWS
cdk deploy
# List all stacks in the app
cdk ls
# Compare deployed stack with current state
cdk diff
# Open CDK documentation
cdk docs

# import individual classes from top-level aws_cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_lambda as lambda_
from aws_cdk import App, Construct, Stack

# If you need many classes from the aws_cdk, you may use a namespace alias of cdk instead of importing individual classes. Avoid doing both.
import aws_cdk as cdk

# Generally, import AWS Construct Libraries using short namespace aliases.
import aws_cdk.aws_s3 as s3

```


The `cdk.json` file tells the CDK Toolkit how to execute your app.




To add additional dependencies, for example other CDK libraries, just add
them to your `requirements.txt` file and rerun the `python -m pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

## Third Party Libraries (constructs)
The CDK team maintains a Construct Library for each AWS service. These libraries are available in multiple languages and can be found in the [AWS Construct Library](https://docs.aws.amazon.com/cdk/api/v2/constructs/construct-library.html) documentation.

AWS CDK library is a language-specific package that provides typed “constructs” (classes) you use to define AWS infrastructure in code. Examples include:

aws-cdk-lib (the main v2 library in TypeScript/JavaScript)
aws-cdk-lib via constructs in Python/Java/.NET

Service-specific modules within the library (e.g., S3, Lambda, DynamoDB constructs)

**Basically it’s the SDK layer that lets you model AWS resources as code, which the CDK then synthesizes into CloudFormation.**

```python
from setuptools import setup

setup(
  name='my-package',
  version='0.0.1',
  install_requires=[
    'aws-cdk-lib==2.14.0',
  ],
  ...
)
```

## Python Idioms
- `snake_case` for variables and functions
- `PascalCase` for classes
- **type hints** for function signatures
- **docstrings** to document functions and classes
- **list comprehensions** and **generator expressions** for concise code
- **context managers** (**with** statements) for resource management
- **logging** instead of print statements for debug output
- **virtual environments** (venv) to manage dependencies
- **requirements.txt** or **pyproject.toml** to specify dependencies
- **pytest** for testing and test discovery
- **black** or **flake8** or **ruff** for code formatting and linting
- **AWS CDK constructs** to define infrastructure as code
- **AWS SAM** for local development and testing of Lambda functions
- **boto3** for AWS SDK interactions in Lambda functions
- **AWS Lambda Powertools** for structured logging, tracing, and metrics in Lambda functions
- **AWS CloudWatch** for monitoring and alerting on Lambda function performance and errors
- **AWS DynamoDB** for serverless NoSQL database needs in Lambda functions
- **AWS S3** for serverless object storage needs in Lambda functions
- **AWS API Gateway** for serverless API management needs in Lambda functions
- **AWS SQS** for serverless message queuing needs in Lambda functions
- **AWS SES** for serverless email sending needs in Lambda functions
- **AWS SNS** for serverless pub/sub messaging needs in Lambda functions
- **AWS CloudWatch Events** for serverless scheduled tasks in Lambda functions
- a trailing underscore for variable names that would otherwise conflict with Python keywords (e.g., lambda_ instead of lambda)
- **double underscores** for “private” variables and methods in classes (e.g., __my_variable)
- **single underscores** for “protected” variables and methods in classes (e.g., _my_variable)
- **all caps** for constants (e.g., MAX_RETRIES)

---
# Project Goals

## Phase 1: Foundation
Get the monolith deployed and working

 Project structure setup (we already have this)
 FastAPI + Mangum basic handler
 SAM template.yaml configuration
 Local dev environment (docker-compose or SAM local)
 First deploy to AWS — "hello world" endpoint


## Phase 2: Auth Service
Central authentication for all your sites

 User table in DynamoDB
 Registration endpoint (hash passwords with passlib)
 Login endpoint (return JWT)
 JWT validation middleware
 Protected route example
 Integrate with one of your sites


## Phase 3: Secret Messages
Encrypted dead-drop for yourself

 Generate pub/priv keypair
 Store private key encrypted with your password in DynamoDB
 Public endpoint: accepts encrypted message, stores in DynamoDB
 Authenticated endpoint: fetches encrypted key, decrypts with password, decrypts message
 Auto-delete after read (optional)
 TTL expiration on messages


## Phase 4: Email Service
SQS-triggered email generation

 SQS queue setup
 Lambda trigger on queue
 SES integration for sending
 Email templates (welcome, notifications, etc.)
 API endpoint to queue emails from your other services


## Phase 5: Scheduled Scraper
Cron-based web scraping

 CloudWatch scheduled event
 BeautifulSoup + httpx scraper logic
 Store results in S3 or DynamoDB
 Notification on completion (SNS or email yourself)


## Phase 6: Markdown → Deploy
Auto-publish markdown docs to your sites

 S3 bucket for markdown uploads
 Lambda trigger on upload
 Markdown → HTML conversion
 Push to GitHub repo via API
 GitHub Pages or Netlify auto-deploys from there


## Phase 7: Logging / Admin Dashboard
Central visibility into your backend

 Log storage (DynamoDB or S3)
 Simple FastAPI admin routes
 Protected with your auth service
 View logs, messages, scraper results


Nice-to-haves (later):
AI API
SES (Simple Email Service) integration
OAuth2 support (Google, GitHub logins)
Rate limiting with DynamoDB
API keys for external access
Plotly charts for scraper data visualization
Multi-device key sync for secret messages

## Dependencies
- fastapi
- starlette streams, in fastapi
- ffmpeg-python - video/audio
- websockets - in fastapi
- mangum
- boto3
- pynamodb
- pydantic - already included with fastapi
- cryptography
- python-jose (or pyjwt) already in fastapi
- passlib
- httpx
- beautifulsoup4
- pandas
- numpy
- pdoc - autodoc to html generator
- markdown2 - for markdown parsing to html


structlog — structured logging, nice output
aws-lambda-powertools — AWS's own library, includes logging, tracing, metrics + cloudwatch is free and integrated
Selenium vs playwright vs hosted browser (browserless.io/scrapingbee,scrapfly)


## Tech Stack
- **Runtime**: Python 3.13
- **Infrastructure**: AWS SAM (not CDK or raw CloudFormation)
- **Compute**: AWS Lambda with Function URLs (no API Gateway)
- **Database**: DynamoDB
- **Dev Environment**: Windows 11, VS Code, Docker Desktop, AWS CLI
- ToDo Later: SQS, SES, SNS, CloudWatch

## Current Structure
```shell
cloud-voyages-lambda/
├── template.yaml
├── samconfig.toml
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── policies/
│   ├── assume_policy.json
│   └── attach_policy.json
└── src/
    ├── __init__.py
    ├── handler.py # controller file
    ├── templates/
    │    ├── admin.html
    │    └── about.html
    ├── static/
    │    ├── style.css
    │    └── logo.png
    ├── request_validator.py
    ├── db_util.py
    ├── users.py
    ├── entity.py
    ├── finance.py
    ├── dynamo.py
    ├── rate_limit.py
    ├── response.py
    ├── request.py
    ├── cache.py
    ├── sam_script.py
    ├── util.py
    ├── middleware.py
    ├── encrypt.py
    ├── oauth.py
    ├── tokens.py
    ├── register.py
    ├── login.py
    ├── logout.py
    ├── refresh_token.py
    ├── forgot_password.py
    ├── reset_password.py
    ├── secret_messages.py
    ├── email.py
    ├── scraper.py
    └──health/
        ├── lambda_health_check.py
        ├── dynamo_health_check.py
        └── site_health_check.py
```

## Other Repo Examples
Zappa
maybe-finance/maybe
actualbudget/actualbudget
firefly-iii
teller.io - screen scraper

## TAbles
Users Table
PK: USER #<user_id>
SK: PROFILE

Attributes:
- email (GSI)
- password_hash
- created_at
- updated_at
Tokens Table (refresh tokens, password reset tokens)
PK: TOKEN#<token_id>
SK: <token_type>  # REFRESH | RESET | INVITE

Attributes:
- user_id
- expires_at (TTL)
- created_at
Secret Messages Table
PK: MSG#<message_id>
SK: <user_id>

Attributes:
- encrypted_payload
- encrypted_response (AI response)
- read: boolean
- created_at
- expires_at (TTL)
Scraper Results Table
PK: SCRAPE#<job_id>
SK: <timestamp>

Attributes:
- source_url
- data (JSON blob or S3 pointer)
- status: PENDING | COMPLETE | FAILED
- created_at
Email Queue (or use SQS instead)
PK: EMAIL#<email_id>
SK: <status>#<timestamp>

Attributes:
- to
- template
- params (JSON)
- sent_at
- created_at 


Login Attempts Table (rate limiting / brute force protection)
PK: LOGIN#<email or ip>
SK: ATTEMPT#<timestamp>

Attributes:
- success: boolean
- ip_address
- user_agent
- created_at
- expires_at (TTL - auto-cleanup after 24h)
Or simpler — just track counts:
PK: LOGIN#<email>
SK: ATTEMPTS

Attributes:
- count
- last_attempt
- locked_until
- expires_at (TTL)
Blacklisted Tokens Table (invalidated JWTs)
PK: BLACKLIST#<token_jti>
SK: TOKEN

Attributes:
- user_id
- reason: LOGOUT | REVOKED | PASSWORD_CHANGE
- created_at
- expires_at (TTL - match token expiry, auto-cleanup)