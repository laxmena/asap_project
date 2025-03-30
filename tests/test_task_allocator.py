import os
import sys
import logging
from datetime import datetime
from redis import Redis
from rq import Queue
import json

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.constants import QueueNames, RedisKeys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_bot_metadata(redis_conn: Redis) -> bool:
    """Set up bot metadata in Redis."""
    try:
        # Bot metadata entries
        bots = [
            {
                "bot_type": "ground_bot",
                "bot_id": "12",
                "altitude": 22,
                "lat": 12.1212,
                "long": -121.234,
                "battery_level": 22.3,
                "status": "available",
                "contains_aid_kit": True,
                "capabilities": "Search - Scans the target disaster area, and collects information such as Photos, Distress voice signal recognition, Identify toxic gas emissions\n"
                              "Assist Rescue - Assists human first responder during the rescue task\n"
                              "Dispatch aid package - Dispatches items such as water, food, first aid kit, to the human survivors."
            },
            {
                "bot_type": "drone_bot",
                "bot_id": "21",
                "altitude": 22,
                "lat": 12.1212,
                "long": -121.234,
                "battery_level": 78.2,
                "status": "available",
                "capabilities": "Search - Scans the target disaster area. It collects and process Images, Thermal images, Hazard detection - such as fire, flood, structural damage."
            },
            {
                "bot_type": "drone_bot",
                "bot_id": "22",
                "altitude": 22,
                "lat": 12.1212,
                "long": -121.234,
                "battery_level": 78.2,
                "status": "available",
                "capabilities": "Search - Scans the target disaster area. It collects and process Images, Thermal images, Hazard detection - such as fire, flood, structural damage."
            }
        ]

        # Store each bot's metadata
        for bot in bots:
            bot_id = bot["bot_id"]
            key = f"{RedisKeys.BOTS_METADATA.value}:{bot_id}"
            redis_conn.set(key, json.dumps(bot))
            logger.info(f"Stored metadata for bot {bot_id}")

        return True
    except Exception as e:
        logger.error(f"Error setting up bot metadata: {str(e)}")
        return False

def send_test_task():
    """Send a test task to the TaskAllocator queue."""
    try:
        # Connect to Redis
        redis_conn = Redis(host='localhost', port=6379)
        
        # Set up bot metadata first
        if not setup_bot_metadata(redis_conn):
            logger.error("Failed to set up bot metadata")
            return False
        
        # Create queue
        q = Queue(QueueNames.TASK_ALLOCATOR.value, connection=redis_conn)
        
        # Test task data
        test_task = {
            "lat": 15.234,
            "long": -122.234,
            "timestamp": int(datetime.now().timestamp()),  # Current timestamp
            "task_type": "search",
            "task_id": 899,
            "context": "reports of human survivor found near collapsed building",
            "priority": 0.99
        }
        
        # Enqueue the task using the correct function path
        job = q.enqueue('src.workers.task_allocator_worker.process_task', test_task)
        logger.info(f"Test task enqueued successfully. Job ID: {job.id}")
        logger.info(f"Task data: {test_task}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending test task: {str(e)}")
        return False

if __name__ == "__main__":
    success = send_test_task()
    if success:
        logger.info("Test completed successfully")
    else:
        logger.error("Test failed") 