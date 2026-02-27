"""User service router combining all user endpoints."""

from fastapi import APIRouter
import os
import boto3
# from fastapi import FastAPI, HTTPException

router = APIRouter()

# Initialize the resource
dynamodb = boto3.resource('dynamodb')
# Pull the table name from the environment variable we set in SAM

@router.get("/resume/{user_id}")
async def get_resume(user_id: str):
    try:
        # Your template uses 'USER#<id>-personaldata' as the PK
        pk_value = f"USER#{user_id}-personaldata"
        
        response = resume_table.get_item(
            Key={
                'pk': pk_value,
                'sk': 'RESUME'
            }
        )
        
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Resume item not found.")
            
        return item
    except Exception as e:
        # Log this to CloudWatch in production
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resume/default")
async def get_default_resume() -> dict:
    try:
        # Your template uses 'USER#<id>-personaldata' as the PK
        pk_value = f"USER#brudow317-personaldata"
        
        response = resume_table.get_item(
            Key={
                'pk': pk_value,
                'sk': 'RESUME'
            }
        )
        
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Resume item not found.")
            
        return item
    except Exception as e:
        # Log this to CloudWatch in production
        raise HTTPException(status_code=500, detail=str(e))