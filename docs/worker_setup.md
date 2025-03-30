# Worker Setup Guide

This guide explains how to set up and run the task allocation workers for the ASAP project.

## Prerequisites

- Redis server running locally (or accessible via network)
- Python 3.8+
- Required Python packages installed (see requirements.txt)

## Environment Setup

1. Create a `.env` file in the project root with the following variables:
```
ANTHROPIC_API_KEY=your_api_key_here
REDIS_URL=redis://localhost:6379  # Optional, defaults to this value
```

## Starting Workers

### Using RQ CLI (Recommended)

The simplest way to start workers is using the RQ CLI:

```bash
# Start a worker for the task allocator queue
rq worker task_allocator

# Start workers for all agent queues
rq worker drone_agent_task ground_agent_task
```

### Using Supervisor (Production)

For production environments, we recommend using Supervisor to manage workers. Here's a sample supervisor configuration:

```ini
[program:task_allocator_worker]
command=rq worker task_allocator
directory=/path/to/project
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/task_allocator.err.log
stdout_logfile=/var/log/task_allocator.out.log
environment=PYTHONPATH="/path/to/project"

[program:drone_agent_worker]
command=rq worker drone_agent_task
directory=/path/to/project
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/drone_agent.err.log
stdout_logfile=/var/log/drone_agent.out.log
environment=PYTHONPATH="/path/to/project"

[program:ground_agent_worker]
command=rq worker ground_agent_task
directory=/path/to/project
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/ground_agent.err.log
stdout_logfile=/var/log/ground_agent.out.log
environment=PYTHONPATH="/path/to/project"
```

### Using Docker Compose

For containerized environments, you can use Docker Compose to manage workers:

```yaml
version: '3'
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  task_allocator_worker:
    build: .
    command: rq worker task_allocator
    environment:
      - REDIS_URL=redis://redis:6379
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis

  drone_agent_worker:
    build: .
    command: rq worker drone_agent_task
    environment:
      - REDIS_URL=redis://redis:6379
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis

  ground_agent_worker:
    build: .
    command: rq worker ground_agent_task
    environment:
      - REDIS_URL=redis://redis:6379
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis
```

## Monitoring Workers

You can monitor workers using the RQ dashboard:

```bash
# Install RQ dashboard
pip install rq-dashboard

# Start the dashboard
rq-dashboard
```

The dashboard will be available at http://localhost:9181 by default.

## Troubleshooting

1. Check Redis connection:
```bash
redis-cli ping
# Should return PONG
```

2. Check worker logs:
```bash
# If using RQ CLI
tail -f /var/log/task_allocator.err.log

# If using Docker
docker-compose logs -f task_allocator_worker
```

3. Common issues:
   - Redis connection errors: Ensure Redis is running and accessible
   - Missing environment variables: Check .env file and environment setup
   - Worker not processing tasks: Check queue names match between publisher and worker 