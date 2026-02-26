from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import database
from schemas import UserCreate
import uuid
import os
from dotenv import load_dotenv
from jinja2 import Template
import resend

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

with open("output.html", "r") as f:
    html = f.read()

template = Template(html)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("DEV_SERVER"), os.getenv("FRONT-END-PROD"), ""],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to your API"}

@app.post("/signup")
async def signup(user: UserCreate):
    query = "SELECT email FROM users WHERE email = :email"
    existing_email = await database.fetch_one(query=query, values={"email": user.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    insert_query = """
    INSERT INTO users (id, email, discount_eligible, created_at)
    VALUES (:id, :email, :discount_eligible, NOW())
    """
    await database.execute(
        query=insert_query,
        values={
            "id": str(uuid.uuid4()),
            "email": user.email,
            "discount_eligible": True
        }
    )

    try:
        resend.Emails.send({
            "from": "team@devolib.com",
            "to": user.email,
            "subject": "Thanks for Joining DevoLib!",
            "html": template.render()
        })
    except Exception as e:
        print(f"Email failed to send: {e}")


    return {"message": "User created successfully"}


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/hi")
async def hi():
    return {"message": "Auth router is working!"}