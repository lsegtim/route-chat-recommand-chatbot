import os

import motor.motor_asyncio
import pandas as pd
from bson import ObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langdetect import detect

from chatbot import initialize_bot, get_response_chatbot

from dotenv import load_dotenv

# show all columns
pd.set_option('display.max_columns', None)

app = FastAPI()

print("Starting server...")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.histomind

data_length = 100000

chatbot = initialize_bot()


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


@app.get("/chatbot/{message}")
async def get_chatbot(message: str):
    # detect language
    language = detect(message)
    if language == "en" or language == "de" or language == "ta":
        response = str(get_response_chatbot(message, chatbot))
    else:
        response = "Sorry, I don't understand that."
    return {"response": response, "language": language}

# 652b9e279c8deef2485bf90c
