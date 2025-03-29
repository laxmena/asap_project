# ASAP Project - Setup Guide

## Prerequisites
Before setting up the project, ensure that you have the following installed:
- **Python 3.8+**
- **Redis Server** (for task queuing)
- **pip** (Python package manager)
- **virtualenv** (recommended for dependency management)

---

## 1. Clone the Repository
```bash
git clone https://github.com/laxmena/drone-harmony-dashboard.git
cd asap_project
```

---

## 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

## 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 4. Install and Run Redis Server
### **Linux/macOS (Homebrew Method for macOS)**
```bash
brew install redis
brew services start redis
```
### **Ubuntu/Debian**
```bash
sudo apt update
sudo apt install redis
sudo systemctl start redis
sudo systemctl enable redis
```
### **Windows (Using Chocolatey)**
```powershell
choco install redis
redis-server
```
### **Verify Redis Installation**
Run the following command to check if Redis is running:
```bash
redis-cli ping
```
If it returns `PONG`, Redis is running successfully.

---

## 5. Start Redis Queue Worker
Open a separate terminal and run:
```bash
rq worker --with-scheduler
```

---

## 6. Set Up Environment Variables
Create a `.env` file in the project root:
```env
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

---

## 7. Run the Project
Start the main system:
```bash
python main.py
```

To test task allocation, enqueue a task manually:
```python
from redis import Redis
from rq import Queue
from agents.search_agent.search import perform_search_task

redis_conn = Redis()
queue = Queue('search_tasks', connection=redis_conn)
job = queue.enqueue(perform_search_task, "disaster_zone_1")
print(f"Task {job.id} added to queue!")
```

---

## 8. Running Tests
```bash
pytest tests/
```

---

## 9. Stopping Services
- Stop the Redis server:
  ```bash
  sudo systemctl stop redis  # Linux
  brew services stop redis  # macOS
  ```
- Stop the virtual environment:
  ```bash
  deactivate
  ```

---

## Additional Notes
- To ensure Redis starts automatically on system reboot, enable Redis as a service:
  ```bash
  sudo systemctl enable redis
  ```
- The project uses **RQ (Redis Queue)** to manage task distribution across agents.
- If you encounter dependency issues, try:
  ```bash
  pip install --upgrade pip
  ```

---

## Troubleshooting
### **Redis Server Not Running?**
- Check if Redis is installed: `redis-server --version`
- Restart Redis: `sudo systemctl restart redis`
- Check Redis logs: `journalctl -u redis --no-pager`

### **Virtual Environment Issues?**
- Run: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
- If activation fails, reinstall virtualenv:
  ```bash
  pip install virtualenv
  ```
