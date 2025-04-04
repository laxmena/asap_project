# ASAP Project Architecture

## Overview
The Autonomous Search and Assistance Protocol (ASAP) system is designed to coordinate multi-agent robotic systems for disaster response. The system consists of drones, ground robots, and a central command that dynamically assigns and reassigns tasks based on real-time sensor data and environmental conditions.

## Components
### 1. Central Command System
- **Responsibilities:** 
  - Task creation
  - Decision-making and coordination
  - Communication with agents and external sources
- **Key Algorithms Used:**
    - TBD
- **Interfaces:**
  - **Input:** Live sensor data, mission parameters, agent status updates
  - **Output:** Assigned tasks to agents, task status updates, mission reports

### 2. Data Aggregator
- **Responsibilities:**
  - Collects and pre-processes data from multiple sources
  - Filters noise and extracts useful features
  - Provides data to command system for decision-making
- **Key Algorithms Used:**
  - Data Fusion (Can look into - Kalman Filters for sensor fusion)
  - Anomaly Detection (TBD)
  - NLP Processing (LLM-based summarization of textual emergency reports)
- **Interfaces:**
  - **Input:** Camera images, thermal imaging, gas sensor data, survivor audio cues, weather data, human reporters
  - **Output:** Structured and cleaned data for command system

### 3. Coordination Agent
- **Responsibilities:**
  - Schedules and assigns tasks dynamically
  - Ensures load balancing across agents
- **Key Algorithms Used:**
  - Task Scheduling (Priority queue + ML Models for optimization)
  - Failure Recovery (Predictive modeling for task reassignment)
- **Interfaces:**
  - **Input:** Task requests from the command system
  - **Output:** Optimized task assignments

### 4. Search Agent (Drones/Ground Robots)
- **Responsibilities:**
  - Identify survivors, hazards, or blocked paths
- **Key AI Models Used:**
  - Human Detection (Google Mediapipe model)
  - [Optional] Object Detection (YOLOv8 for real-time image processing)
  - [Optional] Thermal Image Classification (Model TBD)
  - Gas Leak Detection (Custom Model trained using dataset from https://archive.ics.uci.edu/dataset/360/air+quality. Also explore Pre-trained models in Kaggle)
- **Interfaces:**
  - **Input:** Sensor data from onboard cameras and environmental sensors
  - **Output:** Processed observations and alerts to the command system

### 5. Rescue Agent (Ground Robots/Drones)
- **Responsibilities:**
  - Provide first aid kits, water, and emergency supplies
  - Ground verification system
- **Key AI Models Used:**
  - Gesture/Voice Recognition (MediaPipe + LLM for human interaction)
- **Interfaces:**
  - **Input:** Target location, survivor requests
  - **Output:** Action execution, status reports

## Task Types
- **Search:** Scouting and mapping
- **Survivor Detection:** Identifying and marking survivor locations
- **Hazard Detection:** Gas leaks, fires, structural instability
- **Emergency Supply Delivery:** First aid, water, food

## Communication Mechanism
- **Message Bus (Redis):** Enables async, real-time communication
- **Heartbeats:** Agents send status updates to detect failures
- **Reassignment Strategy:** If an agent fails, tasks get redistributed

<!-- 
## ML/AI Models Used
| Component         | Model/Technology Used |
|------------------|----------------------|
| Search Agent    | MediaPipe, YOLOv8, Custom ML Model |
| Rescue Agent    | MediaPipe, LLM |
| Coordination    | Priority Queue ML, (Later Reinforcement Learning) |
| Command System  | Foundational model-assisted task generation |
| Data Aggregator | Kalman Filters, NLP Summarization | -->

## Simulation Plan
- **Data Inputs:** Pre-collected disaster datasets (thermal images, gas sensor data, etc.)
- **Simulation Tools:** 
  - Custom Python scripts for sensor data emulation
  - Future Simulations:
    - CARLA for autonomous navigation testing
    - Unreal Engine simulation for disaster scenarios

## Deployment Strategy
- **Local Setup:** Run all agents as Python services communicating via Redis/RabbitMQ
- **Future Expansion:** Physical robot integration with ROS2
