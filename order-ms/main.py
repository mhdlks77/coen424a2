from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from database import db
import asyncio
from consumer import consume_events

app = FastAPI(title="Order Microservice")


class Order(BaseModel):
    userId: str
    items: List[str]
    email: str
    deliveryAddress: str

class StatusUpdate(BaseModel):
    status: str

class ContactUpdate(BaseModel):
    email: Optional[str]
    deliveryAddress: Optional[str]

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_events())

@app.post("/orders")
async def create_order(order: Order):
    new_order = {
        "userId": order.userId,
        "items": order.items,
        "email": order.email,
        "deliveryAddress": order.deliveryAddress,
        "status": "under process"
    }
    result = await db.orders.insert_one(new_order)
    new_order["_id"] = str(result.inserted_id)
    return new_order


@app.get("/orders")
async def get_orders(status: Optional[str] = None):
    if status:
        orders = await db.orders.find({"status": status}).to_list(100)
    else:
        orders = await db.orders.find().to_list(100)

    for o in orders:
        o["_id"] = str(o["_id"])
    return orders


@app.put("/orders/{order_id}/status")
async def update_status(order_id: str, body: StatusUpdate):
    result = await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": body.status}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order status updated"}
