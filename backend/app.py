from fastapi import FastAPI, HTTPException, Depends, status
import secrets
import jwt
import hashlib
import os
import dotenv

dotenv.load_dotenv()


app = FastAPI(
    Title = 'Campus' , 
    description= '' , 
    version= '1.0'
    )




@app.get('/')
def root():
    return {'status' : 'running'}

@app.get('/login')
def auth():
    return
