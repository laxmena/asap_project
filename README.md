# ASAP Project

A comprehensive system for autonomous search and rescue operations using coordinated drone and ground agents.

## Project Structure

```
asap_project/
│── agents/  
│   ├── drone_agents/  
│   ├── ground_agents/  
│   ├── coordination_agent/  
│── data_aggregator/  
│── central_command/  
│── perception/  
│── communication/  
│── common/  
│── tests/  
│── datasets/  
│── simulation/  
```

## Setup Instructions

1. Create a Python virtual environment:
```bash
python3.11 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development

- Use `black` for code formatting
- Use `flake8` for linting
- Run tests with `pytest`

## License

TBD
