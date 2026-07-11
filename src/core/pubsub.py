import redis.asyncio as redis
import json
import logging
from typing import Callable, Any

logger = logging.getLogger("RedisPubSub")

class PubSubManager:
    """
    Manages Redis Pub/Sub for high-frequency telemetry and WebSocket broadcasts.
    Replaces the memory-bound list iteration for extreme scaling.
    """
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.pubsub = None
        self.is_connected = False

    async def connect(self):
        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            await self.redis.ping()
            self.is_connected = True
            logger.info("Connected to Redis Pub/Sub broker.")
        except Exception as e:
            logger.warning(f"Could not connect to Redis broker (falling back to memory): {e}")
            self.is_connected = False

    async def publish(self, channel: str, message: dict):
        if self.is_connected:
            await self.redis.publish(channel, json.dumps(message))
        else:
             pass # Fallback handled by the caller

    async def subscribe(self, channel: str, callback: Callable[[dict], Any]):
        """
        Background task that listens to a Redis channel and fires the callback.
        """
        if not self.is_connected:
             return

        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(channel)
        logger.info(f"Subscribed to Redis channel: {channel}")

        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    await callback(data)
                except Exception as e:
                    logger.error(f"Error processing pubsub message: {e}")

    async def disconnect(self):
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
        self.is_connected = False

pubsub_manager = PubSubManager()
