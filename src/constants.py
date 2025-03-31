from enum import Enum

class QueueNames(Enum):
    MAIN_QUEUE = "main_queue"  # Single queue for all tasks

class RedisKeys(Enum):
    BOTS_METADATA = "bots:metadata"
    TASK_ALLOCATOR_PROMPT = "task_allocator:prompt"
    EVENTS = "events"
    EVENTS_BY_LOCATION = "events:location"
    WEATHER_DATA = "weather:data"
    WEATHER_LAST_UPDATE = "weather:last_update"

class BotTypes(Enum):
    DRONE = "drone_bot"
    GROUND = "ground_bot"

# LLM Configuration
LLM_MODEL = "claude-3-5-sonnet-latest"
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY" 

# Firebase Path in the Realtime Database
path = '/hackproject'  
firebase_auth = "src/utils/firdb-2025-firebase-adminsdk-fbsvc-a566cdf29f.json"
database_url = 'https://firdb-2025-default-rtdb.firebaseio.com/'
# LLM_MODEL = "claude-3-5-sonnet-latest"
LLM_MODEL = "claude-3-opus-20240229"
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"

class DataSourceType(Enum):
    WEATHER = "weather"
    DRONE_BOT = "drone_bot"
    GROUND_BOT = "ground_bot"
    HUMAN_REPORT = "human_report"

class DataType(Enum):
    IMAGE = "image"
    THERMAL_IMAGE = "thermal_image"
    HUMAN_REPORT = "human_report"
    GAS_SENSOR = "gas_sensor"
    WEATHER = "weather" 