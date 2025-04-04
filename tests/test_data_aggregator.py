import os
import sys
import logging
from redis import Redis
from rq import Queue
from datetime import datetime
import base64
import io
from PIL import Image
import json

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.constants import QueueNames, RedisKeys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_bot_metadata(redis_conn: Redis) -> bool:
    """Set up bot metadata in Redis."""
    try:
        # Bot metadata entries
        bots = [
            {
                "bot_type": "ground_bot",
                "bot_id": "Ground Bot Alpha",
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
                "bot_type": "ground_bot",
                "bot_id": "Ground Bot Beta",
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
                "bot_id": "Rescue Drone 1",
                "altitude": 100,
                "lat": 18.332,
                "long": -121.234,
                "battery_level": 18.2,
                "status": "available",
                "capabilities": "Search - Scans the target disaster area. It collects and process Images, Thermal images, Hazard detection - such as fire, flood, structural damage."
            },
            {
                "bot_type": "drone_bot",
                "bot_id": "Rescue Drone 2",
                "altitude": 22,
                "lat": 16.1212,
                "long": -123.234,
                "battery_level": 98.2,
                "status": "not_available",
                "capabilities": "Search - Scans the target disaster area. It collects and process Images, Thermal images, Hazard detection - such as fire, flood, structural damage."
            },
            {
                "bot_type": "drone_bot",
                "bot_id": "Rescue Drone 3",
                "altitude": 200,
                "lat": 13.1212,
                "long": -119.234,
                "battery_level": 78.2,
                "status": "avvailable",
                "capabilities": "Search - Scans the target disaster area, can take pictures of the area. It collects and process Images, Thermal images, Hazard detection - such as fire, flood, structural damage."
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


def send_test_image_data(image_path):
    """Send a test image data to the main queue."""
    try:
        # Connect to Redis
        redis_conn = Redis(host='localhost', port=6379)
        
        # Create queue
        q = Queue(QueueNames.MAIN_QUEUE.value, connection=redis_conn)
        image_base64 = encode_image_to_base64(image_path)
        
        # Example image data
        test_data = {
            "data_id": "test_image_1",
            "task_type": "data_aggregator",
            "data_type": "image",
            "lat": 37.7749, 
            "long": -122.4194,
            "timestamp": datetime.now().isoformat(),
            "source": "drone_234",
            "image_base64": image_base64,
        }
        
        # Enqueue the data
        job = q.enqueue('src.workers.main_worker.process_task', test_data)
        logger.info(f"Test image data enqueued successfully. Job ID: {job.id}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending test image data: {str(e)}")
        return False

def send_test_thermal_data(image_path):
    """Send a test thermal image data to the main queue."""
    logger.info(f"Sending test thermal data")
    try:
        # Connect to Redis
        redis_conn = Redis(host='localhost', port=6379)
        
        # Create queue
        q = Queue(QueueNames.MAIN_QUEUE.value, connection=redis_conn)
        thermal_image_base64 = encode_image_to_base64(image_path)
        
        # Example thermal data
        test_data = {
            "data_id": "test_thermal_1",
            "task_type": "data_aggregator",
            "data_type": "thermal_image",
            "lat": 37.7749, 
            "long": -122.4194,
            "timestamp": datetime.now().isoformat(),
            "source": "drone_1123123",
            "thermal_image_base64": thermal_image_base64,
        }
        
        # Enqueue the data
        job = q.enqueue('src.workers.main_worker.process_task', test_data)
        logger.info(f"Test thermal image data enqueued successfully. Job ID: {job.id}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending test thermal data: {str(e)}")
        return False

def send_test_human_report():
    """Send a test human report to the main queue."""
    try:
        # Connect to Redis
        redis_conn = Redis(host='localhost', port=6379)
        
        # Create queue
        q = Queue(QueueNames.MAIN_QUEUE.value, connection=redis_conn)
        
        # Example human report
        test_data = {
            "data_id": "test_report_1",
            "task_type": "data_aggregator",
            "data_type": "human_report",
            "lat": 37.7749, 
            "long": -122.4194,
            "timestamp": datetime.now().isoformat(),
            "source": "lakshmanan",
            "report": {
                "type": "survivor_found",
                "details": "Fire in the building, lots of smoke and flames. Surivors in top floor of the building. Need immediate assistance.",
                "urgency": "high"
            }
        }
        
        # Enqueue the data
        job = q.enqueue('src.workers.main_worker.process_task', test_data)
        logger.info(f"Test human report enqueued successfully. Job ID: {job.id}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending test human report: {str(e)}")
        return False

def send_test_gas_data():
    """Send a test gas sensor data to the main queue."""
    try:
        # Connect to Redis
        redis_conn = Redis(host='localhost', port=6379)
        
        # Create queue
        q = Queue(QueueNames.MAIN_QUEUE.value, connection=redis_conn)
        
        # Example gas sensor data
        test_data = {
            "data_id": "test_gas_1",
            "task_type": "data_aggregator",
            "data_type": "gas_sensor",
            "lat": 37.7749, 
            "long": -122.4194,
            "timestamp": datetime.now().isoformat(),
            "source": "drone_1",
            "gas_levels": {
                "co": 40,
                "co2": 1233,
                "ch4": 10000,
                "h2s": 80
            },
            "hazard_level": "low"
        }
        
        # Enqueue the data
        job = q.enqueue('src.workers.main_worker.process_task', test_data)
        logger.info(f"Test gas sensor data enqueued successfully. Job ID: {job.id}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending test gas data: {str(e)}")
        return False

def encode_image_to_base64(image_path, max_size=(640, 480), quality=60, max_file_size_kb=100):
    """
    Resize and compress image before encoding to base64.
    
    Args:
        image_path: Path to the image file
        max_size: Maximum dimensions (width, height) for the image
        quality: JPEG quality (1-100, higher means better quality but larger size)
        max_file_size_kb: Maximum allowed file size in KB
    
    Returns:
        Base64 encoded string of the compressed image
    """
    
    try:
        
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(os.path.dirname(image_path), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate temp file path
        original_filename = os.path.basename(image_path)
        temp_filename = f"compressed_{original_filename}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        # Open and resize image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Resize image while maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes buffer with compression
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
            
            # Get the compressed image data
            compressed_data = buffer.getvalue()
            
            # If still too large, reduce quality further
            while len(compressed_data) > max_file_size_kb * 1024 and quality > 20:
                quality -= 10
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
                compressed_data = buffer.getvalue()
                logger.info(f"Reducing quality to {quality} to meet size requirements")
            
            # Save compressed image to temp file
            with open(temp_path, 'wb') as f:
                f.write(compressed_data)
            logger.info(f"Saved compressed image to: {temp_path}")
            
            # Encode to base64
            encoded_image = base64.b64encode(compressed_data).decode("utf-8")
            
            # Log compression results
            original_size = os.path.getsize(image_path)
            compressed_size = len(compressed_data)
            reduction = (original_size - compressed_size) / original_size * 100
            logger.info(f"Image compression: {original_size/1024:.1f}KB -> {compressed_size/1024:.1f}KB ({reduction:.1f}% reduction)")
            
            return encoded_image
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise

if __name__ == "__main__":
    redis_conn = Redis(host='localhost', port=6379)
    setup_bot_metadata(redis_conn)
    
    image_path = "datasets/sensor_data_samples/camera_images/wild_fire.jpeg"
    thermal_image_path = "datasets/sensor_data_samples/thermal_images/thermal_image.jpeg"        
    # Run all tests
    # send_test_image_data(image_path)
    # send_test_thermal_data(thermal_image_path)
    send_test_human_report()
    # send_test_gas_data() 