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
from src.agents.data_aggregator import DataAggregator
from src.agents.command_system_agent import CommandSystemAgent
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_task(task_data):
    """Process a task based on its type."""
    try:
        # Add processing timestamp
        task_data["processing_started_at"] = datetime.now().isoformat()
        
        # Get task type
        task_type = task_data.get("task_type")
        
        if task_type == "task_allocator":
            task_allocator = TaskAllocator()
            success = task_allocator.process_task(task_data)
        elif task_type == "data_aggregator":
            data_aggregator = DataAggregator()
            logger.info(f"Processing data aggregator task")
            success = data_aggregator.process_data(task_data)
        elif task_type == "command_system":
            command_system = CommandSystemAgent()
            success = command_system.process_data(task_data)
            success = True
        else:
            logger.error(f"Unknown task type: {task_type}")
            return False
            
        if success:
            logger.info(f"Successfully processed {task_type} task")
        else:
            logger.error(f"Failed to process {task_type} task")
            
        return success
    except Exception as e:
        logger.error(f"Error processing task: {str(e)}")
        return False

def main():
    """Main worker function."""
    redis_conn = Redis(host='localhost', port=6379)
    q = Queue(QueueNames.MAIN_QUEUE.value, connection=redis_conn)
    worker = Worker([q])
    worker.work()

if __name__ == '__main__':
    main() 