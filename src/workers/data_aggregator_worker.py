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
from src.agents.data_aggregator import DataAggregator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_data(data):
    """Process a single data item from the queue."""
    try:
        # Add processing timestamp
        data["processing_started_at"] = datetime.now().isoformat()
        
        data_aggregator = DataAggregator()
        success = data_aggregator.process_data(data)
        
        if success:
            logger.info(f"Successfully processed data from source {data.get('source')}")
        else:
            logger.error(f"Failed to process data from source {data.get('source')}")
            
        return success
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return False

def main():
    """Main worker function."""
    redis_conn = Redis(host='localhost', port=6379)
    q = Queue(QueueNames.DATA_AGGREGATOR.value, connection=redis_conn)
    worker = Worker([q])
    worker.work()

if __name__ == '__main__':
    main() 