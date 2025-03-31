import json
import logging
from typing import Any, Dict, List, Optional
from redis import Redis
from rq import Queue
from dotenv import load_dotenv
import os
from datetime import datetime

from src.constants import QueueNames, RedisKeys

logger = logging.getLogger(__name__)

class RedisUtils:
    def __init__(self):
        """Initialize Redis connection and queue."""
        load_dotenv()
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = Redis.from_url(redis_url)
        self.queue = Queue(QueueNames.MAIN_QUEUE.value, connection=self.redis_client)

    def _get_bot_key(self, bot_id: str) -> str:
        """Generate Redis key for a specific bot."""
        return f"{RedisKeys.BOTS_METADATA.value}:{bot_id}"

    def get_bot_metadata(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Fetch metadata for a specific bot."""
        try:
            data = self.redis_client.get(self._get_bot_key(bot_id))
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error fetching bot metadata for bot {bot_id}: {str(e)}")
            return None

    def set_bot_metadata(self, bot_id: str, metadata: Dict[str, Any]) -> bool:
        """Store metadata for a specific bot."""
        try:
            self.redis_client.set(self._get_bot_key(bot_id), json.dumps(metadata))
            return True
        except Exception as e:
            logger.error(f"Error storing bot metadata for bot {bot_id}: {str(e)}")
            return False

    def delete_bot_metadata(self, bot_id: str) -> bool:
        """Delete metadata for a specific bot."""
        try:
            self.redis_client.delete(self._get_bot_key(bot_id))
            return True
        except Exception as e:
            logger.error(f"Error deleting bot metadata for bot {bot_id}: {str(e)}")
            return False

    def get_all_bots_metadata(self) -> List[Dict[str, Any]]:
        """Fetch metadata for all bots."""
        try:
            # Get all keys matching the pattern
            keys = self.redis_client.keys(f"{RedisKeys.BOTS_METADATA.value}:*")
            metadata_list = []
            
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    metadata_list.append(json.loads(data))
            
            return metadata_list
        except Exception as e:
            logger.error(f"Error fetching all bots metadata: {str(e)}")
            return []

    def enqueue_task(self, task_type: str, task_data: Dict[str, Any]) -> bool:
        """Enqueue a task with its type."""
        try:
            # Add task type to the data
            task_data["task_type"] = task_type
            
            # Enqueue to the main queue
            job = self.queue.enqueue('src.workers.main_worker.process_task', task_data)
            
            logger.info(f"Task enqueued to main queue with job ID: {job.id}")
            return True
        except Exception as e:
            logger.error(f"Error enqueueing task: {str(e)}")
            return False

    def store_event(self, event_id: str, event_data: Dict[str, Any]) -> bool:
        """Store event data in Redis."""
        try:
            self.redis_client.set(event_id, json.dumps(event_data))
            return True
        except Exception as e:
            logger.error(f"Error storing event {event_id}: {str(e)}")
            return False

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Fetch event data from Redis."""
        try:
            data = self.redis_client.get(event_id)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error fetching event {event_id}: {str(e)}")
            return None

    def delete_event(self, event_id: str) -> bool:
        """Delete event data from Redis."""
        try:
            self.redis_client.delete(event_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting event {event_id}: {str(e)}")
            return False

    def store_weather_data(self, location_key: str, weather_data: Dict[str, Any]) -> bool:
        """Store weather data in Redis."""
        try:
            self.redis_client.set(
                f"{RedisKeys.WEATHER_DATA.value}:{location_key}",
                json.dumps(weather_data)
            )
            self.redis_client.set(
                f"{RedisKeys.WEATHER_LAST_UPDATE.value}:{location_key}",
                str(datetime.now().timestamp())
            )
            return True
        except Exception as e:
            logger.error(f"Error storing weather data for {location_key}: {str(e)}")
            return False

    def get_weather_data(self, location_key: str) -> Optional[Dict[str, Any]]:
        """Fetch weather data from Redis."""
        try:
            data = self.redis_client.get(f"{RedisKeys.WEATHER_DATA.value}:{location_key}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error fetching weather data for {location_key}: {str(e)}")
            return None

    def get_weather_last_update(self, location_key: str) -> Optional[float]:
        """Get timestamp of last weather data update."""
        try:
            timestamp = self.redis_client.get(f"{RedisKeys.WEATHER_LAST_UPDATE.value}:{location_key}")
            if timestamp:
                return float(timestamp)
            return None
        except Exception as e:
            logger.error(f"Error fetching weather last update for {location_key}: {str(e)}")
            return None 