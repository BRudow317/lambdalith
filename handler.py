# handler.py
from fastapi import FastAPI
from mangum import Mangum
from app import app

app(FastAPI())

handler = Mangum(app)
