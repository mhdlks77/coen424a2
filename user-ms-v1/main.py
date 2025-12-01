from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import db
from bson import ObjectId
from rabbitmq import publish_event

app = FastAPI(title="User Microservice v1")


class User(BaseModel):
    email: str
    deliveryAddress: str

class UpdateEmail(BaseModel):
    email: str

class UpdateAddress(BaseModel):
    deliveryAddress: str


@app.post("/users")
async def create_user(user: User):
    new_user = {
        "email": user.email,
        "deliveryAddress": user.deliveryAddress
    }
    result = await db.users.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)
    return new_user


@app.put("/users/{user_id}/email")
async def update_email(user_id: str, body: UpdateEmail):
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"email": body.email}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    await publish_event(
        "user.email.updated",
        {"user_id": user_id, "email": body.email}
    )

    return {"message": "Email updated (v1)"}



@app.put("/users/{user_id}/address")
async def update_address(user_id: str, body: UpdateAddress):
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"deliveryAddress": body.deliveryAddress}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    await publish_event(
        "user.address.updated",
        {"user_id": user_id, "deliveryAddress": body.deliveryAddress}
    )

    return {"message": "Address updated (v1)"}
