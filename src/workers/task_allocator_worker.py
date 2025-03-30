import os
import sys
import logging
from rq import Worker, Queue
from redis import Redis
from datetime import datetime

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.constants import QueueNames
from src.agents.task_allocator import TaskAllocator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_task(task_data):
    """Process a single task from the queue."""
    try:
        # Add processing timestamp
        task_data["processing_started_at"] = datetime.now().isoformat()
        
        task_allocator = TaskAllocator()
        success = task_allocator.process_task(task_data)
        
        if success:
            logger.info(f"Successfully processed task {task_data.get('task_id')}")
        else:
            logger.error(f"Failed to process task {task_data.get('task_id')}")
            
        return success
    except Exception as e:
        logger.error(f"Error processing task: {str(e)}")
        return False

def main():
    """Main worker function."""
    redis_conn = Redis(host='localhost', port=6379)
    q = Queue(QueueNames.TASK_ALLOCATOR.value, connection=redis_conn)
    worker = Worker([q])
    worker.work()

if __name__ == '__main__':
    main() 