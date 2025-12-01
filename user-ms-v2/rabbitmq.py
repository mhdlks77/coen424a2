import aio_pika
import os
from dotenv import load_dotenv
import json

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")


async def publish_event(event_type: str, payload: dict):
    """
    Publishes an event to RabbitMQ (fanout exchange).
    """
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()

        # Declare fanout exchange for user updates
        exchange = await channel.declare_exchange(
            "user_updates", aio_pika.ExchangeType.FANOUT, durable=True
        )

        message = aio_pika.Message(
            body=json.dumps({"type": event_type, "data": payload}).encode()
        )

        await exchange.publish(message, routing_key="")
