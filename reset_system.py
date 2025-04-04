import os
import subprocess
from src.utils.redis import RedisUtils
from src.utils.logging_utils import LoggerSetup

def reset_system():
    # Initialize logger
    logger = LoggerSetup.get_logger(name=__name__)
    logger.info("[RESET SCRIPT] Starting system reset")
    
    try:
        # Clear RQ queues
        logger.info("[RESET SCRIPT] Clearing RQ queues")
        redis_utils = RedisUtils()
        redis_utils.redis_client.delete('rq:queue:main_queue')
        logger.info("[RESET SCRIPT] Successfully cleared RQ queues")
        
        # Flush all Redis data
        logger.info("[RESET SCRIPT] Flushing all Redis data")
        redis_utils.redis_client.flushall()
        logger.info("[RESET SCRIPT] Successfully flushed Redis data")
        
        logger.info("[RESET SCRIPT] System reset completed successfully")
        
    except Exception as e:
        logger.error(f"[RESET SCRIPT] Error during system reset: {str(e)}")
        raise

if __name__ == "__main__":
    reset_system() 