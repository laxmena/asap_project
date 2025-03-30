import json
import logging
from typing import Any, Dict, List, Optional
from redis import Redis
from rq import Queue
from dotenv import load_dotenv
import os

from src.constants import QueueNames, RedisKeys

logger = logging.getLogger(__name__)

class RedisUtils:
    def __init__(self):
        """Initialize Redis connection and queues."""
        load_dotenv()
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = Redis.from_url(redis_url)
        self.queues = {
            QueueNames.TASK_ALLOCATOR.value: Queue(QueueNames.TASK_ALLOCATOR.value, connection=self.redis_client),
            QueueNames.DRONE_AGENT.value: Queue(QueueNames.DRONE_AGENT.value, connection=self.redis_client),
            QueueNames.GROUND_AGENT.value: Queue(QueueNames.GROUND_AGENT.value, connection=self.redis_client),
        }

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

    # TODO: Add more helper functions for differernt operations - enqueue_dataaggregator, enqueue_task_allocator, enqueue_task_allocator, etc.
    def enqueue_task(self, queue_name: str, task_data: Dict[str, Any]) -> bool:
        """Enqueue a task to a specific queue."""
        try:
            if queue_name not in self.queues:
                logger.error(f"Queue {queue_name} not found")
                return False
            
            # For agent queues, we'll use a simple function name since the task is already processed
            if queue_name.endswith('_agent_task'):
                # TODO: Update the module to actually invoke the task in Agents
                job = self.queues[queue_name].enqueue('process_agent_task', task_data)
            else:
                # For task allocator queue, use the full function path
                job = self.queues[queue_name].enqueue('src.tasks.task_allocator', task_data)
            
            logger.info(f"Task enqueued to {queue_name} with job ID: {job.id}")
            return True
        except Exception as e:
            logger.error(f"Error enqueueing task to {queue_name}: {str(e)}")
            return False 