import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from src.utils.redis import RedisUtils


class GroundBotAgent:
    def __init__(self):
        self._setup()
        self.llm = LLMSingleton.get_instance()

    def process_task(self, payload: Dict[str, Any]) -> bool:
        # Print the task and confirmation of task
        logger.info(f"[Ground Bot Agent] Task: {payload}")
        logger.info(f"[Ground Bot Agent] Task Confirmation")

        # Sleep for 10 seconds
        time.sleep(10)

        # Get sensor data
        sensor_data = self.get_sensor_data()
        logger.info(f"[Ground Bot Agent] Sensor Data: {sensor_data}")

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
        
        return True
    
    def _setup(self):
        self.scenarios = {
            'normal': {
                'temperature': 25,
                'CO': 5,
                'CO2': 400,
                'smoke_particles': 0,
                'has_fire': False
            },
            'fire': {
                'temperature': 150,
                'CO': 150,
                'CO2': 6000,
                'smoke_particles': 300,
                'has_fire': True,
                'fire_location': {'lat': 37.7749, 'long': -121.6694}
            },
            'smoke_only': {
                'temperature': 30,
                'CO': 50,
                'CO2': 1000,
                'smoke_particles': 200,
                'has_fire': False
            },
            'multiple_fires': {
                'temperature': 200,
                'CO': 300,
                'CO2': 8000,
                'smoke_particles': 400,
                'has_fire': True,
                'fire_locations': [
                    {'lat':38.111, 'long': -112.4422},
                    {'lat': 32.7349, 'long': -123.3344}
                ]
            }
        }

    def get_sensor_data(self, scenario='normal'):
        """Generate sensor data for the specified scenario"""
        if scenario not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario}")

        data = self.scenarios[scenario].copy()
        return {
            'temperature': data['temperature'],
            'CO': data['CO'],
            'CO2': data['CO2'],
            'smoke_particles': data['smoke_particles'],
            'heat_sensors': self._generate_heat_sensors(data)
        }

    def _generate_heat_sensors(self, scenario_data):
        """Generate heat sensor readings based on scenario"""
        sensors = []
        if scenario_data['has_fire']:
            if 'fire_location' in scenario_data:
                sensors.append({
                    'lat': scenario_data['fire_location']['lat'],
                    'long': scenario_data['fire_location']['long'],
                    'temperature': scenario_data['temperature'],
                    'area': 25
                })
            elif 'fire_locations' in scenario_data:
                for location in scenario_data['fire_locations']:
                    sensors.append({
                        'lat': location['lat'],
                        'long': location['long'],
                        'temperature': scenario_data['temperature'],
                        'area': 25
                    })
        return sensors