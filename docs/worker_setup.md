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
REDIS_URL=redis://localhost:6379 
```

## Starting Workers

### Using RQ CLI (Recommended)

The simplest way to start workers is using the RQ CLI:

```bash
python src/workers/main_worker.py
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