class DroneBotAgent:
    def __init__(self, image_path_prefix=""):
        self.image_path_prefix = image_path_prefix

    def process_task(self, payload: Dict[str, Any]) -> bool:
        # Print the task and confirmation of task
        logger.info(f"[Drone Bot Agent] Task: {payload}")
        logger.info(f"[Drone Bot Agent] Task Confirmation")
        
        # Sleep for 10 seconds
        time.sleep(10)

        self.image_pairs = {
            'Forest3': (f'{self.image_path_prefix}Forest3_camera.png', f'{self.image_path_prefix}Forest3_thermal.png'),
            'Forest2': (f'{self.image_path_prefix}Forest2_camera.png', f'{self.image_path_prefix}Forest2_thermal.png'),
            'Forest': (f'{self.image_path_prefix}Forest_camera.png', f'{self.image_path_prefix}Forest_thermal.png'),
            'Smoke': (f'{self.image_path_prefix}Smoke_camera.png', f'{self.image_path_prefix}Smoke_thermal.png'),
            'Man': (f'{self.image_path_prefix}Man_camera.png', f'{self.image_path_prefix}Man_thermal.png')
        }
        camera_img, thermal_img = self.get_random_image_pair()
                
        data_aggregator_payload = {
            "data_id": random.randint(1000000000, 9999999999),
            "task_type": "data_aggregator",
            "data_type": "gas_sensor",
            "lat": 37.7749, 
            "long": -122.4194,
            "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data
        }
        
        # Feedback loop
        # Send the Data to DataAggregator
        self.redis_utils.enqueue_task(
            "data_aggregator",
            data_aggregator_payload
        )
        
        sleep(3)
        
        
        
        return True

    def get_random_image_pair(self):
        prefix = random.choice(list(self.image_pairs.keys()))
        camera_img, thermal_img = self.image_pairs[prefix]
        return camera_img, thermal_img