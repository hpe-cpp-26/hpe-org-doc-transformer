import json
import logging
from typing import Callable, Awaitable
import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractQueue, AbstractRobustConnection, AbstractChannel
from config.settings import get_settings
import asyncio

settings = get_settings()
logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self):
        self.rabbitmq_url = settings.rabbitmq_url
        self.connection: AbstractRobustConnection | None = None 
        self.channel: AbstractChannel | None = None
        self.queue_name = settings.rabbitmq_queue
    
    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(
                self.rabbitmq_url,
                reconnect_interval=5,
                )
            self.channel = await self.connection.channel()
            logger.info(f"Connected to RabbitMQ: {self.rabbitmq_url}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def declare_queue(self)-> AbstractQueue:
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        queue= await self.channel.declare_queue(self.queue_name, durable=True)
        logger.info(f"Declared queue: {self.queue_name}")
        return queue

    async def consume_messages(self,  callback: Callable[[dict], Awaitable[None]],prefetch_count: int = 1)->None:
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        await self.channel.set_qos(prefetch_count=prefetch_count)

        queue = await self.declare_queue()

        async def message_callback(message: AbstractIncomingMessage):
            async with message.process(requeue=False):
                try:
                    payload = json.loads(message.body.decode("utf-8"))
                    logger.info(f"Received message: {payload}")
                    await callback(payload)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    raise

        await queue.consume(message_callback)
        logger.info(f"Consuming from '{self.queue_name}'...")

        await asyncio.Future() 
        
    async def close(self) -> None:
        """Close connection."""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")
