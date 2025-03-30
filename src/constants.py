from enum import Enum

class QueueNames(Enum):
    TASK_ALLOCATOR = "task_allocator"
    DRONE_AGENT = "drone_bot_agent_task"
    GROUND_AGENT = "ground_bot_agent_task"
    

class RedisKeys(Enum):
    BOTS_METADATA = "bots:metadata"
    TASK_ALLOCATOR_PROMPT = "task_allocator:prompt"

class BotTypes(Enum):
    DRONE = "drone_bot"
    GROUND = "ground_bot"

# LLM Configuration
LLM_MODEL = "claude-3-5-sonnet-latest"
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY" 