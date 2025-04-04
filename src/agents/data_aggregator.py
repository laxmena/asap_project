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
from src.utils.logging_utils import LoggerSetup

class DataAggregator:
    def __init__(self, session_id: Optional[str] = None):
        """Initialize DataAggregator with Redis connection and LLM setup."""
        self.redis_utils = RedisUtils()
        self.llm = LLMSingleton.get_instance()
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.weather_api_url = "http://api.openweathermap.org/data/2.5/weather"
        self.logger = LoggerSetup.get_logger(session_id=session_id, name=__name__)

    def _get_prompt_template(self, data_type: str) -> Optional[str]:
        """Read and prepare the prompt template based on data type."""
        try:
            self.logger.info(f"[DATA AGGREGATOR] Getting prompt template for {data_type}")
            prompt_file = f"prompts/data_aggregator/interpret_{data_type}_prompt.txt"
            with open(prompt_file, "r") as f:
                prompt_template = f.read()
            return prompt_template
        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error reading prompt template for {data_type}: {str(e)}")
            return None

    def _replace_payload_in_prompt(self, prompt_template: str, payload: Dict[str, Any]) -> str:
        try:
            payload_str = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
            return prompt_template.replace("<replace_payload>", payload_str)
        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error replacing payload in prompt: {str(e)}")
            return ""

    def _process_image_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            self.logger.info("[DATA AGGREGATOR] Processing image data")
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
            # self.logger.debug(f"[DATA AGGREGATOR] Generated prompt: {prompt}")

            self.logger.info("[DATA AGGREGATOR] Invoking LLM for image processing")
            response = self.llm.invoke(prompt)
            self.logger.debug(f"[DATA AGGREGATOR] LLM Response: {json.dumps(json.loads(response.content), indent=4)}")
            
            return json.loads(response.content)
        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error processing image data: {str(e)}")
            return None

    def _process_thermal_image_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self.logger.info("[DATA AGGREGATOR] Processing thermal image data")
        try:
            prompt_template = self._get_prompt_template(DataType.THERMAL_IMAGE.value)
            
            if not prompt_template:
                return None
                
            self.logger.info("[DATA AGGREGATOR] Prompt template fetched")
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
            # self.logger.debug(f"[DATA AGGREGATOR] Generated prompt: {prompt}")
            
            self.logger.info("[DATA AGGREGATOR] Invoking LLM for thermal image processing")
            response = self.llm.invoke(prompt)
            self.logger.debug(f"[DATA AGGREGATOR] LLM Response: {json.dumps(json.loads(response.content), indent=4)}")
            
            return json.loads(response.content)
        
        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error processing thermal image data: {str(e)}")
            return None

    def _process_human_report(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            self.logger.info("[DATA AGGREGATOR] Processing human report")
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

            # self.logger.debug(f"[DATA AGGREGATOR] Generated prompt: {prompt}")
            self.logger.info("[DATA AGGREGATOR] Invoking LLM for human report processing")
            response = self.llm.invoke(prompt)
            self.logger.debug(f"[DATA AGGREGATOR] LLM Response: {json.dumps(json.loads(response.content), indent=4)}")
            
            return json.loads(response.content)
        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error processing human report: {str(e)}")
            return None

    def _process_gas_sensor_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            self.logger.info("[DATA AGGREGATOR] Processing gas sensor data")
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

            # self.logger.debug(f"[DATA AGGREGATOR] Generated prompt: {prompt}")
            self.logger.info("[DATA AGGREGATOR] Invoking LLM for gas sensor data processing")
            response = self.llm.invoke(prompt)
            self.logger.debug(f"[DATA AGGREGATOR] LLM Response: {json.dumps(json.loads(response.content), indent=4)}")

            return json.loads(response.content)
        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error processing gas sensor data: {str(e)}")
            return None

    def _fetch_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Fetch weather data from OpenWeather API."""
        try:
            self.logger.info(f"[DATA AGGREGATOR] Fetching weather data for coordinates: {lat}, {lon}")
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.weather_api_key,
                "units": "metric"
            }
            response = requests.get(self.weather_api_url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            self.logger.debug(f"[DATA AGGREGATOR] Weather data: {json.dumps(weather_data, indent=4)}")
            return weather_data
        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error fetching weather data: {str(e)}")
            return None

    def _store_event(self, event_data: Dict[str, Any]) -> bool:
        """Store event data in Redis with geospatial indexing."""
        try:
            self.logger.info("[DATA AGGREGATOR] Storing event data")
            event_id = f"event:{datetime.now().timestamp()}"
            self.redis_utils.redis_client.set(event_id, json.dumps(event_data))
            
            # self.logger.debug(f"[DATA AGGREGATOR] Event data: {json.dumps(event_data, indent=4)}")

            self.logger.info("[DATA AGGREGATOR] Adding to geospatial index")
            self.redis_utils.redis_client.geoadd(
                RedisKeys.EVENTS_BY_LOCATION.value,
                [ event_data["lon"], event_data["lat"], event_id]
            )
            self.logger.info("[DATA AGGREGATOR] Successfully added event data to geospatial index")

            return True
        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error storing event: {str(e)}")
            return False

    def _get_nearby_events(self, lat: float, lon: float, radius: float = 1.0) -> List[Dict[str, Any]]:
        """Get events within a specified radius of coordinates."""
        try:
            self.logger.info(f"[DATA AGGREGATOR] Getting nearby events for coordinates: {lat}, {lon}")
            event_ids = self.redis_utils.redis_client.geosearch(
                RedisKeys.EVENTS_BY_LOCATION.value,
                longitude=lon,
                latitude=lat,
                radius=radius,
                unit="km"
            )

            events = []
            for event_id in event_ids:
                event_data = self.redis_utils.redis_client.get(event_id)
                if event_data:
                    events.append(json.loads(event_data))

            self.logger.debug(f"[DATA AGGREGATOR] Found {len(events)} nearby events")
            return events
        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error getting nearby events: {str(e)}")
            return []

    def process_data(self, data: Dict[str, Any]) -> bool:
        """Process incoming data and store events."""
        try:
            self.logger.info("[DATA AGGREGATOR] Starting data processing")
            # self.logger.debug(f"[DATA AGGREGATOR] Input data: {json.dumps(data, indent=4)}")
            
            data_type = data.get("data_type")
            processed_data = None

            self.logger.info(f"[DATA AGGREGATOR] Processing data of type {data_type}")
            
            if data_type in ["image", "jpeg"]:
                processed_data = self._process_image_data(data)
            elif data_type == "thermal_image":
                processed_data = self._process_thermal_image_data(data)
            elif data_type == "human_report":
                processed_data = self._process_human_report(data)
            elif data_type == "gas_sensor":
                processed_data = self._process_gas_sensor_data(data)

            if not processed_data:
                self.logger.error(f"[DATA AGGREGATOR] Failed to process data of type {data_type}")
                return False

            event_data = {
                "source": data.get("source"),
                "timestamp": data.get("timestamp"),
                "lat": data.get("lat"),
                "lon": data.get("long"),
                "data_type": data_type,
                "processed_data": processed_data
            }
            
            self.logger.debug(f"[DATA AGGREGATOR] Event data: {json.dumps(event_data, indent=4)}")
            
            if not self._store_event(event_data):
                self.logger.error("[DATA AGGREGATOR] Failed to store event")
                return False

            nearby_events = self._get_nearby_events(
                float(data.get("lat")),
                float(data.get("long"))
            )

            command_system_payload = {
                "events": nearby_events,
            }
            
            self.logger.debug(f"[DATA AGGREGATOR] Command system payload: {json.dumps(command_system_payload, indent=4)}")
            
            self.logger.info("[DATA AGGREGATOR] Forwarding to command system")
            self.redis_utils.enqueue_task(
                "command_system",
                command_system_payload
            )

            self.logger.info("[DATA AGGREGATOR] Processing completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"[DATA AGGREGATOR] Error processing data: {str(e)}")
            return False 