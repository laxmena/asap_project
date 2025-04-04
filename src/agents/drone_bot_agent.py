import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from src.utils.redis import RedisUtils
from src.utils.logging_utils import LoggerSetup
import time
import random
import os
import io
import base64
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DroneBotAgent:
    def __init__(self, session_id: Optional[str] = None, image_path_prefix="/Users/laxmena/workplace/github/asap_project/datasets/sensor_data_samples/camera_images/"):
        self.image_path_prefix = image_path_prefix
        self.redis_utils = RedisUtils()
        self.logger = LoggerSetup.get_logger(session_id=session_id, name=__name__)
        self._setup_image_pairs()

    def _setup_image_pairs(self):
        self.logger.info("[DRONE BOT AGENT] Setting up image pairs")
        self.image_pairs = {
            'Forest3': (f'{self.image_path_prefix}Forest3_camera.png', f'{self.image_path_prefix}Forest3_thermal.png'),
            'Forest2': (f'{self.image_path_prefix}Forest2_camera.png', f'{self.image_path_prefix}Forest2_thermal.png'),
            'Forest': (f'{self.image_path_prefix}Forest_camera.png', f'{self.image_path_prefix}Forest_thermal.png'),
            'Smoke': (f'{self.image_path_prefix}Smoke_camera.png', f'{self.image_path_prefix}Smoke_thermal.png'),
            'Man': (f'{self.image_path_prefix}Man_camera.png', f'{self.image_path_prefix}Man_thermal.png')
        }

    def encode_image_to_base64(self, image_path, max_size=(640, 480), quality=60, max_file_size_kb=100):
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
            self.logger.info(f"[DRONE BOT AGENT] Processing image: {image_path}")
            
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
                    self.logger.info(f"[DRONE BOT AGENT] Reducing quality to {quality} to meet size requirements")
                
                # Save compressed image to temp file
                with open(temp_path, 'wb') as f:
                    f.write(compressed_data)
                self.logger.info(f"[DRONE BOT AGENT] Saved compressed image to: {temp_path}")
                
                # Encode to base64
                encoded_image = base64.b64encode(compressed_data).decode("utf-8")
                
                # Log compression results
                original_size = os.path.getsize(image_path)
                compressed_size = len(compressed_data)
                reduction = (original_size - compressed_size) / original_size * 100
                self.logger.info(f"[DRONE BOT AGENT] Image compression: {original_size/1024:.1f}KB -> {compressed_size/1024:.1f}KB ({reduction:.1f}% reduction)")
                
                return encoded_image
        except Exception as e:
            self.logger.error(f"[DRONE BOT AGENT] Error processing image: {str(e)}")
            raise

    def process_task(self, payload: Dict[str, Any]) -> bool:
        self.logger.info("[DRONE BOT AGENT] Starting task processing")
        # self.logger.debug(f"[DRONE BOT AGENT] Input payload: {json.dumps(payload, indent=4)}")

        self.logger.info("[DRONE BOT AGENT] Simulating task execution (sleeping for 10s)")
        time.sleep(10)

        self.logger.info("[DRONE BOT AGENT] Selecting random image pair")
        camera_img, thermal_img = self.get_random_image_pair()
        self.logger.debug(f"[DRONE BOT AGENT] Selected images: {camera_img}, {thermal_img}")
                
        self.logger.info("[DRONE BOT AGENT] Processing camera image")
        data_aggregator_payload = {
            "data_id": random.randint(1000000000, 9999999999),
            "task_type": "data_aggregator",
            "data_type": "image",
            "lat": 37.7749, 
            "long": -122.4194,
            "timestamp": datetime.now().isoformat(),
            "image_base64": self.encode_image_to_base64(camera_img)
        }
        
        self.logger.info("[DRONE BOT AGENT] Forwarding camera image to DataAggregator")
        self.redis_utils.enqueue_task(
            "data_aggregator",
            data_aggregator_payload
        )
        
        time.sleep(3)
        
        self.logger.info("[DRONE BOT AGENT] Processing thermal image")
        data_aggregator_payload = {
            "data_id": random.randint(1000000000, 9999999999),
            "task_type": "data_aggregator",
            "data_type": "thermal_image",
            "lat": 37.7749, 
            "long": -122.4194,
            "timestamp": datetime.now().isoformat(),
            "thermal_image_base64": self.encode_image_to_base64(thermal_img)
        }
        
        self.logger.info("[DRONE BOT AGENT] Forwarding thermal image to DataAggregator")
        self.redis_utils.enqueue_task(
            "data_aggregator",
            data_aggregator_payload
        )
        
        self.logger.info("[DRONE BOT AGENT] Task completed successfully")
        return True

    def get_random_image_pair(self):
        self.logger.info("[DRONE BOT AGENT] Selecting random image pair")
        prefix = random.choice(list(self.image_pairs.keys()))
        camera_img, thermal_img = self.image_pairs[prefix]
        return camera_img, thermal_img