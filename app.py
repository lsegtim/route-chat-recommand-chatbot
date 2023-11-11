import json
import os
from datetime import datetime
from datetime import timedelta
from typing import List

import motor.motor_asyncio
import pandas as pd
from bson import ObjectId
from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from langdetect import detect
from pydantic import BaseModel, Field

from chatbot import initialize_bot, get_response_chatbot
from filtering import filter_data
from nearest_locations import sort_by_distance_from_current_location
from shortest_path import find_shortest_path

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

# load environment variables
from dotenv import load_dotenv

load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.histomind

data_length = 100000

from recommander import get_rec

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


# const userSchema = new Schema(
#     userName: { type: String },
#     email: { type: String },
#     password: { type: String },
#   { collection: "users" }

class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str = Field(...)
    password: str = Field(...)
    username: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "652b9e279c8deef2485bf8f1",
                "email": "Justin.Diaz@gmail.com",
                "password": "v^5BXk2C",
                "username": "JustinDiaz"
            }
        }


@app.get("/users", response_description="List all users", response_model=List[UserModel])
async def list_users():
    users = await db["users"].find().to_list(data_length)
    return users


# const locationSchema = new Schema(
#     _id: { type: Schema.Types.ObjectId, ref: "User" },
#     name: { type: String },
#     description: { type: String },
#     imageUrl: { type: String },
#     city: { type: String },
#     province: { type: String },
#     openTime: { type: String },
#     closeTime: { type: String },
#     latitude: { type: String },
#     longitude: { type: String },
#     accessibility: { type: String },
#     historical_context: { type: String },
#     hands_on_activities: { type: String },
#     rating: { type: String },
#   { collection: "locations" }

class LocationModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    description: str = Field(...)
    imageUrl: str = Field(...)
    city: str = Field(...)
    province: str = Field(...)
    openTime: str = Field(...)
    closeTime: str = Field(...)
    latitude: str = Field(...)
    longitude: str = Field(...)
    accessibility: str = Field(...)
    historical_context: str = Field(...)
    hands_on_activities: str = Field(...)
    rating: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

        schema_extra = {
            "example": {
                "_id": "60f4d5c5b5f0f0e5e8b2b5c9",
                "name": "Rideekanda Forest Monastery",
                "description": "An archaeological site with ancient ruins and inscriptions, providing insight into the region's historical Buddhist presence.",
                "imageUrl": "https://www.rideekanda.com/uploads/2022/1/rideekanda_forest_monastery_sri_lanka_53.jpg",
                "city": "Matale",
                "province": "Central",
                "openTime": "8:00 AM",
                "closeTime": "5:00 PM",
                "latitude": "7.3167",
                "longitude": "80.6333",
                "accessibility": "Wheelchair-accessible car park, Wheelchair-accessible entrance",
                "historical_context": "Ancient Buddhist monastery",
                "hands_on_activities": "Photography, Sightseeing, Relaxing",
                "rating": "4.7"
            }
        }


# List all foods
@app.get("/locations", response_description="List all locations", response_model=List[LocationModel])
async def list_locations():
    locations = await db["locations"].find().to_list(data_length)
    return locations


# const interactionSchema = new Schema(
#     userId: { type: Schema.Types.ObjectId, ref: "User" },
#     locationId: { type: Schema.Types.ObjectId, ref: "Location" },
#     action: { type: String },
#   { collection: "interactions" }

class InteractionModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    location_id: PyObjectId = Field(default_factory=PyObjectId)
    rating: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "60f4d5c5b5f0f0e5e8b2b5c9",
                "user_id": "60f4d5c5b5f0f0e5e8b2b5c9",
                "location_id": "60f4d5c5b5f0f0e5e8b2b5c9",
                "rating": "view"
            }
        }


@app.get("/interactions", response_description="List all interactions", response_model=List[InteractionModel])
async def list_interaction():
    feedbacks = await db["interactions"].find().to_list(data_length)
    return feedbacks


# user login model
class UserLoginModel(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "TaylorDeleon",
                "password": "b)5RyXTm"
            }
        }


# login
@app.post("/login")
async def login(user: UserLoginModel = Body(...)):
    try:
        user = await db["users"].find_one({"username": user.username, "password": user.password})
        if user:
            return {"success": True, "user_id": str(user["_id"])}
        else:
            return {"success": False, "message": "Invalid username or password"}
    except Exception as e:
        print(e)
        return {"success": False, "message": "Invalid username or password"}


# sign up model
class UserSignUpModel(BaseModel):
    email: str = Field(...)
    password: str = Field(...)
    username: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "Justin.Diaz@example.com",
                "password": "v^5BXk2C",
                "username": "JustinDiaz"
            }
        }


# sign up
@app.post("/sign-up")
async def sign_up(user: UserSignUpModel = Body(...)):
    try:
        user = await db["users"].insert_one({"username": user.username, "password": user.password, "email": user.email})
        if user:
            return {"success": True, "user_id": str(user.inserted_id)}
        else:
            return {"success": False, "message": "Invalid username or password"}
    except Exception as e:
        print(e)
        return {"success": False, "message": "Invalid username or password"}


base_url = "http://localhost:8000/"
save_path = "data/"


# Load data
@app.get("/load-data")
async def load_data(request: Request):
    users = await list_users()
    interactions = await list_interaction()
    locations = await list_locations()

    users = pd.DataFrame(users)
    interactions = pd.DataFrame(interactions)
    locations = pd.DataFrame(locations)

    users.to_csv(save_path + "users.csv", index=False)
    interactions.to_csv(save_path + "interactions.csv", index=False)
    locations.to_csv(save_path + "locations.csv", index=False)

    aggregate_data()
    process_data()
    # pre_process()
    # update_log()

    return {"status": "success"}


def aggregate_data():
    # read csv
    users_df = pd.read_csv(save_path + "users.csv")
    interactions_df = pd.read_csv(save_path + "interactions.csv")
    locations_df = pd.read_csv(save_path + "locations.csv")

    print(users_df.head())
    print(interactions_df.head())
    print(locations_df.head())

    # merge users and interactions
    df = pd.merge(users_df, interactions_df, left_on='_id', right_on='user_id', how='inner')
    print(df.head())

    # merge df and locations
    df = pd.merge(df, locations_df, left_on='location_id', right_on='_id', how='inner')
    print(df.head())

    # save to csv
    df.to_csv(save_path + "aggregate.csv", index=False)

    print("\n\nName of the file: aggregate")
    print(df.head())


def process_data():
    # load csv
    df = pd.read_csv(save_path + "aggregate.csv")

    # _id_x,email,password,username,_id_y,user_id,location_id,rating_x,_id,name,description,imageUrl,city,province,openTime,closeTime,latitude,longitude,accessibility,historical_context,hands_on_activities,planning,rating_y

    # drop _id_x, email, password, _id_y, user_id, location_id, _id, imageUrl
    df.drop(columns=['_id_x', 'email', 'password', 'username', '_id_y', '_id', 'imageUrl'],
            inplace=True)

    # # rename columns name_x -> food, name_y -> cuisine
    # df.rename(columns={'name_x': 'food_name', 'name_y': 'cuisine', 'food': 'food_id'}, inplace=True)

    # save to csv
    df.to_csv(save_path + "processed.csv", index=False)


def update_log():
    # create txt if not exists and write to it f.write("Last updated: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    if not os.path.exists(save_path + "log.txt"):
        f = open(save_path + "log.txt", "w")
        f.close()

    # open txt and clean write to it
    f = open(save_path + "log.txt", "w")
    f.write("Last updated: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    f.close()


def load_log():
    # load txt
    f = open(save_path + "log.txt", "r")
    read_data = f.read()
    print(read_data)
    f.close()

    # extract datetime
    new_datetime = read_data.split("Last updated: ")[1]

    # convert to datetime
    new_datetime = datetime.strptime(new_datetime, "%d/%m/%Y %H:%M:%S")

    # if last update was more than 1 hour ago
    if datetime.now() - new_datetime > timedelta(hours=1):
        return True
    else:
        return False


# Recommendation
@app.get("/recommendation/{user_id}")
async def get_recommendation(user_id: str, num_of_rec: int = 5):
    if num_of_rec:
        recommendation, user_stat = get_rec(user_id, num_of_rec=num_of_rec)
    else:
        recommendation, user_stat = get_rec(user_id, num_of_rec=5)

    update_log()
    return {"recommendations": recommendation}


# Load data and Recommendation
@app.get("/recommendation-load/{user_id}")
async def get_recommendation_load(user_id: str, num_of_rec: int = 5):
    users = await list_users()
    interactions = await list_interaction()
    locations = await list_locations()

    users = pd.DataFrame(users)
    interactions = pd.DataFrame(interactions)
    locations = pd.DataFrame(locations)

    users.to_csv(save_path + "users.csv", index=False)
    interactions.to_csv(save_path + "interactions.csv", index=False)
    locations.to_csv(save_path + "locations.csv", index=False)

    aggregate_data()
    process_data()
    # pre_process()
    update_log()

    if num_of_rec:
        recommendation, user_stat = get_rec(user_id, num_of_rec=num_of_rec)
    else:
        recommendation, user_stat = get_rec(user_id, num_of_rec=5)

    # from location dataframe keep only ids in recommadation
    locations = pd.read_csv(save_path + "locations.csv")
    locations = locations[locations['_id'].isin(recommendation)]

    # Convert DataFrame to a dictionary
    df_dict = locations.to_dict(orient='records')

    # Convert dictionary to JSON string
    json_string = json.dumps(df_dict)

    # save json file
    with open('recommendation.json', 'w') as outfile:
        json.dump(df_dict, outfile)

    # open json file
    with open('recommendation.json') as json_file:
        json_string = json.load(json_file)

    return json_string


@app.get("/chatbot/{message}")
async def get_chatbot(message: str):
    # detect language
    language = detect(message)
    if language == "en" or language == "de" or language == "ta":
        response = str(get_response_chatbot(message, chatbot))
    else:
        response = "Sorry, I don't understand that."
    return {"response": response, "language": language}


# {
#   authenticated: false,
#   username: "",
#   password: "",
#   user_id: "",
#   latitude: 0.0,
#   longitude: 0.0,
#   destination_id: "",
#   distanceRadiusValue: 10.0,
#   updatedData: {
#   "Time Restrictions": "Not selected",
#   "Accessibility": "Not selected",
#   "Historical Contexts": "Not selected",
#   "Hands-On Activities": "Not selected"
# }

# shortest path model
class ShortestPathModel(BaseModel):
    # authenticated: bool = Field(...)
    # username: str = Field(...)
    # password: str = Field(...)
    user_id: str = Field(...)
    latitude: float = Field(...)
    longitude: float = Field(...)
    destination_id: str = Field(...)
    distanceRadiusValue: float = Field(...)
    updatedData: dict = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "652b9e279c8deef2485bf90a",
                "latitude": 6.91,
                "longitude": 79.85,
                "destination_id": "652b9d229c8deef2485bf8e9",
                "distanceRadiusValue": 50.0,
                "updatedData": {
                    "Time Restrictions": "0.00AM - 0.00PM",
                    "Accessibility": "Not selected",
                    "Historical Contexts": "Ancient Buddhist monastery",
                    "Hands-On Activities": "Photography, Sightseeing, Relaxing"
                }
            }
        }


# Shortest Path
@app.post("/shortest-path")
async def get_shortest_path(shortest_path: ShortestPathModel = Body(...)):
    locations = await list_locations()

    locations = pd.DataFrame(locations)

    locations.to_csv(save_path + "locations.csv", index=False)

    # location_backup = locations[['_id', 'name', 'latitude', 'longitude']]

    filtered_data = filter_data(shortest_path, locations)

    # keep only _id, name, latitude, longitude
    filtered_data = filtered_data[['_id', 'name', 'latitude', 'longitude']]

    # save dataframe
    filtered_data.to_csv("filtered_data.csv", index=False)

    filtered_data = find_shortest_path(shortest_path, filtered_data)

    # save dataframe
    filtered_data.to_csv("shortest_path.csv", index=False)

    # open dataframe to json
    filtered_data = pd.read_csv("shortest_path.csv")

    # Convert DataFrame to a dictionary
    df_dict = filtered_data.to_dict(orient='records')

    # Convert dictionary to JSON string
    json_string = json.dumps(df_dict)

    # save json file
    with open('shortest_path.json', 'w') as outfile:
        json.dump(df_dict, outfile)

    # open json file
    with open('shortest_path.json') as json_file:
        json_string = json.load(json_file)

    return json_string


# Nearest Location by Current Location Model
class NearestLocationModel(BaseModel):
    latitude: float = Field(...)
    longitude: float = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "latitude": 6.91,
                "longitude": 79.85
            }
        }


# Nearest Location by Current Location
@app.post("/nearest-location")
async def get_nearest_location(nearest_location: NearestLocationModel = Body(...), num_of_rec: int = 10,
                               distance: float = 0):
    locations = await list_locations()

    locations = pd.DataFrame(locations)

    locations.to_csv(save_path + "locations.csv", index=False)

    current_location = (nearest_location.latitude, nearest_location.longitude)

    filtered_data = sort_by_distance_from_current_location(locations, current_location, distance)

    filtered_data = filtered_data.head(num_of_rec)

    # save dataframe
    filtered_data.to_csv("nearest_location.csv", index=False)

    # open dataframe to json
    filtered_data = pd.read_csv("nearest_location.csv")

    # Convert DataFrame to a dictionary
    df_dict = filtered_data.to_dict(orient='records')

    # Convert dictionary to JSON string
    json_string = json.dumps(df_dict)

    # save json file
    with open('nearest_location.json', 'w') as outfile:
        json.dump(df_dict, outfile)

    # open json file
    with open('nearest_location.json') as json_file:
        json_string = json.load(json_file)

    return json_string

# 652b9e279c8deef2485bf90c
