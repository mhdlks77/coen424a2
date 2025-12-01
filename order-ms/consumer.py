import aio_pika
import asyncio
import json
from database import db
import os
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")


async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        event_type = data["type"]
        payload = data["data"]

        if event_type == "user.email.updated":
            await update_orders_email(payload["email"], payload["user_id"])

        elif event_type == "user.address.updated":
            await update_orders_address(payload["deliveryAddress"], payload["user_id"])


async def update_orders_email(new_email: str, user_id: str):
    await db.orders.update_many(
        {"userId": user_id},
        {"$set": {"email": new_email}}
    )


async def update_orders_address(new_address: str, user_id: str):
    await db.orders.update_many(
        {"userId": user_id},
        {"$set": {"deliveryAddress": new_address}}
    )


async def consume_events():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    # Same exchange from user services
    exchange = await channel.declare_exchange(
        "user_updates", aio_pika.ExchangeType.FANOUT, durable=True
    )

    # Create queue for order service (durable)
    queue = await channel.declare_queue("order_sync_queue", durable=True)

    # Bind to the exchange
    await queue.bind(exchange)

    print("Order MS is listening for user update events...")

    await queue.consume(handle_message)

    return connection
