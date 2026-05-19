# AI-Enhanced Generator Digital Twin for Real-Time Monitoring and Predictive Maintenance

## Overview

This project presents an AI-enhanced Digital Twin framework for real-time generator monitoring, operational analysis, anomaly detection, and predictive maintenance. The system creates a virtual representation of a physical generator using real-time sensor inputs, mathematical modeling, degradation analysis, and machine learning-based analytics.

The framework continuously monitors operational parameters such as voltage, current, RPM, vibration, and temperature to simulate generator behavior, evaluate equipment condition, detect abnormal operating states, and support intelligent maintenance planning.

---

# Features

- Real-time generator monitoring
- Electrical performance analysis
- Thermal condition monitoring
- Generator degradation estimation
- Health index calculation
- Remaining useful life prediction
- Machine learning-based anomaly detection
- Predictive maintenance recommendations
- Flask-based dashboard visualization
- ESP32 sensor integration support
- Real-time USB serial communication

---

# System Architecture

The proposed architecture consists of:

- Sensor Layer
- ESP32 Data Acquisition Layer
- Generator Digital Twin Engine
- Electrical Model
- Thermal Model
- Degradation Model
- Machine Learning Layer
- Dashboard Visualization

---

# Technologies Used

| Technology | Purpose |
|---|---|
| Python | Digital twin implementation |
| Flask | Dashboard backend |
| HTML/CSS | Dashboard frontend |
| NumPy | Mathematical computations |
| Scikit-learn | Machine learning anomaly detection |
| Chart.js | Real-time graph visualization |
| ESP32 | Sensor data acquisition |
| PySerial | USB serial communication |

---

# Real-Time Parameters Monitored

- Voltage
- Current
- RPM
- Winding Temperature
- Ambient Temperature
- Vibration
- Cooling Status

---

# Mathematical Models Implemented

The digital twin framework uses:

- Generator power equations
- Efficiency calculations
- Copper loss estimation
- Thermal heat transfer equations
- Hotspot temperature estimation
- Health index calculation
- Remaining useful life estimation
- Machine learning-based anomaly detection

---

# Dashboard Features

- Live operational monitoring
- Generator performance graphs
- Health index visualization
- Active fault alerts
- Maintenance recommendations
- Real-time operational analytics

---

# Project Structure

```bash
project/
│
├── prototype-dashboard/
│   ├── app.py
│   ├── requirements.txt
│   │
│   ├── templates/
│   │   └── generator_dashboard.html
│   │
│   ├── twin-models/
│   │   ├── integrated_generator_twin.py
│   │   └── sensor_based_twin.py
│   │
│   ├── sensor-data/
│   │
│   └── venv/
│
└── README.md
```

---

# File Descriptions

| File | Description |
|---|---|
| integrated_generator_twin.py | Demonstration-based generator digital twin using simulated operational data |
| sensor_based_twin.py | Real-time generator digital twin implementation using ESP32 sensor inputs |
| app.py | Flask-based dashboard application |
| generator_dashboard.html | Dashboard frontend interface |
| requirements.txt | Python project dependencies |

---

# Digital Twin Modes

## 1. Demonstration Mode

The `integrated_generator_twin.py` file demonstrates the generator digital twin framework using simulated sensor data.

Run using:

```bash
python integrated_generator_twin.py
```

---

## 2. Real-Time Monitoring Mode

The `sensor_based_twin.py` file enables real-time monitoring using ESP32-connected sensor inputs and live operational data.

Run using:

```bash
python sensor_based_twin.py
```

---

# Hardware Components

The prototype setup includes:

- DC Motor (Used as Generator)
- ESP32 Development Board
- Voltage Sensor
- Current Sensor (ACS712)
- Temperature Sensor (LM35)
- Load Resistor/Bulb
- Cooling Fan
- USB Communication Interface

---

# Installation

## Create Virtual Environment

```bash
python -m venv venv
```

---

## Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Dashboard

```bash
python app.py
```

Open in browser:

```bash
http://127.0.0.1:5000
```

---

# Real-Time Sensor Communication

The real-time implementation receives operational data from ESP32 through serial communication using JSON-formatted sensor readings.

Example JSON sensor data:

```json
{
  "voltage": 230,
  "current": 6.5,
  "rpm": 1500,
  "temperature": 58,
  "ambient_temperature": 30,
  "vibration": 0.3,
  "cooling_active": true
}
```

---

# Prototype Demonstration

A functional prototype of the proposed generator digital twin framework has been successfully developed to demonstrate:

- Real-time operational monitoring
- Thermal and degradation analysis
- Machine learning-based anomaly detection
- Predictive maintenance recommendations
- Dashboard-based visualization

---

# Future Enhancements

- Wireless IoT communication
- MQTT-based cloud integration
- Remote dashboard access
- Historical operational data logging
- Advanced deep learning-based analytics
- Industrial-scale deployment

---

# GitHub Repository

The complete implementation, dashboard visualization, and prototype demonstration source code are available through the GitHub repository associated with this project.

---

# License

This project is developed for educational, research, and demonstration purposes.
