import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import base64
from src.utils.redis import RedisUtils
from src.utils.llm import LLMSingleton
from src.constants import DataSourceType, DataType, RedisKeys, QueueNames
from time import sleep

logger = logging.getLogger(__name__)

class DataAggregator:
    def __init__(self):
        """Initialize DataAggregator with Redis connection and LLM setup."""
        self.redis_utils = RedisUtils()
        self.llm = LLMSingleton.get_instance()
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.weather_api_url = "http://api.openweathermap.org/data/2.5/weather"

    def _get_prompt_template(self, data_type: str) -> Optional[str]:
        """Read and prepare the prompt template based on data type."""
        try:
            logger.info(f"Getting prompt template for {data_type}")
            prompt_file = f"prompts/data_aggregator/interpret_{data_type}_prompt.txt"
            with open(prompt_file, "r") as f:
                prompt_template = f.read()
            return prompt_template
        except Exception as e:
            logger.error(f"Error reading prompt template for {data_type}: {str(e)}")
            return None

    def _replace_payload_in_prompt(self, prompt_template: str, payload: Dict[str, Any]) -> str:
        try:
            payload_str = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
            return prompt_template.replace("<replace_payload>", payload_str)
        except Exception as e:
            logger.error(f"Error replacing payload in prompt: {str(e)}")
            return ""

    def _process_image_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            prompt_template = self._get_prompt_template(DataType.IMAGE.value)
            if not prompt_template:
                return None

            payload = {
                "role": "user",
                "content": [
                    {  
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "mime",
                            "data": data.get("image_base64"),
                        },
                        "context": {
                            "lat": data.get("lat"),
                            "long": data.get("long"),
                            "timestamp": data.get("timestamp"),
                            "source": data.get("source")
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt_template,
                    },
                ],
            }
            prompt = json.dumps(payload, indent=4, ensure_ascii=False, default=str)

            #pretty print the prompt
            # print(prompt)
            response = self.llm.invoke(prompt)
            logger.info("Response: ",response)
            
            # pretty print the response
            print(json.dumps(json.loads(response.content), indent=4))
            
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error processing image data: {str(e)}")
            return None

    def _process_thermal_image_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info(f"Processing thermal image data")
        try:
            prompt_template = self._get_prompt_template(DataType.THERMAL_IMAGE.value)

            
            if not prompt_template:
                return None
                
            logger.info(f"Prompt template fetched")
            payload = {
                "role": "user",
                "content": [
                    {  
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "mime",
                            "data": data.get("thermal_image_base64"),
                        },
                        "context": {
                            "lat": data.get("lat"),
                            "long": data.get("long"),
                            "timestamp": data.get("timestamp"),
                            "source": data.get("source")
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt_template,
                    },
                ],
            }
            
            prompt = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
            response = self.llm.invoke(prompt)
            
            logger.debug(f"Response: {json.dumps(json.loads(response.content), indent=4)}")
            return json.loads(response.content)
        
        except Exception as e:
            logger.error(f"Error processing thermal image data: {str(e)}")
            return None

    def _process_human_report(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            prompt_template = self._get_prompt_template(DataType.HUMAN_REPORT.value)
            if not prompt_template:
                return None

            payload = {
                "role": "user",
                "content": [
                    {
                        "human_report": data.get("report"),
                        "context": {
                            "lat": data.get("lat"),
                            "long": data.get("long"),
                            "timestamp": data.get("timestamp"),
                            "source": data.get("source")
                        }
                    },
                ],
            }

            prompt = self._replace_payload_in_prompt(prompt_template, payload)
            if not prompt:
                return None

            response = self.llm.invoke(prompt)
            logger.info(f"Response: ", response)
            
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error processing human report: {str(e)}")
            return None

    def _process_gas_sensor_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            prompt_template = self._get_prompt_template(DataType.GAS_SENSOR.value)
            if not prompt_template:
                return None

            payload = {
                "gas_levels": data.get("gas_levels"),
                "context": {
                    "lat": data.get("lat"),
                    "long": data.get("long"),
                    "timestamp": data.get("timestamp"),
                    "source": data.get("source")
                }
            }

            prompt = self._replace_payload_in_prompt(prompt_template, payload)
            if not prompt:
                return None

            response = self.llm.invoke(prompt)
            logger.info(f"Response: {json.dumps(json.loads(response.content), indent=4)}")

            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error processing gas sensor data: {str(e)}")
            return None

    def _fetch_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Fetch weather data from OpenWeather API."""
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.weather_api_key,
                "units": "metric"
            }
            response = requests.get(self.weather_api_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return None

    def _store_event(self, event_data: Dict[str, Any]) -> bool:
        """Store event data in Redis with geospatial indexing."""
        try:
            # Store event data
            event_id = f"event:{datetime.now().timestamp()}"
            self.redis_utils.redis_client.set(event_id, json.dumps(event_data))
            
            # Pretty print the event data
            logger.debug(f"[STORE EVENT] Event data: {json.dumps(event_data, indent=4)}")

            logger.info(f"Adding to geospatial index")
            logger.debug(f"Event data: {event_data}")
            
            # Add to geospatial index
            self.redis_utils.redis_client.geoadd(
                RedisKeys.EVENTS_BY_LOCATION.value,
                [ event_data["lon"], event_data["lat"], event_id]
            )
            logger.info(f"Successfully added event data to geospatial index")

            return True
        except Exception as e:
            logger.error(f"Error storing event: {str(e)}")
            return False

    def _get_nearby_events(self, lat: float, lon: float, radius: float = 1.0) -> List[Dict[str, Any]]:
        """Get events within a specified radius of coordinates."""
        try:
            # Get event IDs within radius
            event_ids = self.redis_utils.redis_client.geosearch(
                RedisKeys.EVENTS_BY_LOCATION.value,
                longitude=lon,
                latitude=lat,
                radius=radius,
                unit="km"
            )

            # Fetch event data
            events = []
            for event_id in event_ids:
                event_data = self.redis_utils.redis_client.get(event_id)
                if event_data:
                    events.append(json.loads(event_data))

            return events
        except Exception as e:
            logger.error(f"Error getting nearby events: {str(e)}")
            return []

    def process_data(self, data: Dict[str, Any]) -> bool:
        """Process incoming data and store events."""
        try:
            data_type = data.get("data_type")
            processed_data = None

            logger.info(f"Processing data of type {data_type}")
            
            # weather_data = self._fetch_weather_data(data.get("lat"), data.get("long"))
            
            # Process based on data type
            if data_type in ["image", "jpeg"]:
                processed_data = self._process_image_data(data)
            elif data_type == "thermal_image":
                logger.info(f"Processing thermal image data")
                processed_data = self._process_thermal_image_data(data)
            elif data_type == "human_report":
                processed_data = self._process_human_report(data)
            elif data_type == "gas_sensor":
                processed_data = self._process_gas_sensor_data(data)

            if not processed_data:
                logger.error(f"Failed to process data of type {data_type}")
                return False

            # Store processed event
            event_data = {
                "source": data.get("source"),
                "timestamp": data.get("timestamp"),
                "lat": data.get("lat"),
                "lon": data.get("long"),
                "data_type": data_type,
                "processed_data": processed_data
            }
            # Pretty print the event data
            logger.debug(f"Event data: {json.dumps(event_data, indent=4)}")
            
            if not self._store_event(event_data):
                logger.error("Failed to store event")
                return False

            # Get nearby events and forward to command system
            nearby_events = self._get_nearby_events(
                float(data.get("lat")),
                float(data.get("long"))
            )

            command_system_payload = {
                "events": nearby_events,
            }
            # pretty print the command system payload
            logger.debug(f"Command system payload: {json.dumps(command_system_payload, indent=4)}")
            
            # Forward to command system
            self.redis_utils.enqueue_task(
                "command_system",
                command_system_payload
            )

            return True

        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False 