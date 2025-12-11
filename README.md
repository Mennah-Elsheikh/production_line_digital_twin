# Production Line Digital Twin

An industrial-grade Discrete Event Simulation (DES) of a manufacturing production line. This Digital Twin replicates real-world dynamics including machine failures, warm-up periods, and operational costs, empowered by AI for automated optimization and validation logic for real-world accuracy.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://digital-twin-line.streamlit.app/)

## Key Features

### 🏭 Industrial-Grade Simulation
- **Multi-Stage Line**: Cutting → Drilling → Assembly → Painting.
- **Realistic Dynamics**: 
  - Stochastic processing times (Exponential/Normal).
  - Machine Breakdowns (MTBF/MTTR).
  - Configurable Warm-up Period (discard transient data).
- **Economics**: Tracks Labor, Energy, Downtime, and WIP Holding costs.

### 🧠 AI & Optimization
- **Automated Optimization**: Grid Search algorithm (`--ai-optimize`) explores 80+ configurations to find the optimal balance between *Throughput* and *CapEx*.
- **Bottleneck Detection**: Advanced multi-criteria scoring (Utilization + Queue + Wait + Cycle Time) to identify constraints.

### 🔄 Digital Twin Validation
- **Real vs Simulated**: Compare the simulation's output against real-world production data (CSV).
- **Validation Score**: Automatic scoring of accuracy (Throughput/Lead Time error).
- **Visual Validation**: Interactive overlay of Real vs Simulated distributions.

### 📊 Visualization & UI
- **Streamlit Web App**: Control everything from a browser based UI.
- **Real-time Animation**: Watch products flow through the line with queue visualization.
- **Interactive Dashboards**: Plotly charts for Utilization, WIP, and Financials.

## Installation

### 1. Clone & Setup
```bash
git clone <repo-url>
cd production_line_digital_twin
pip install -r requirements.txt
```

### 2. Dependencies
- `simpy` (Simulation Engine)
- `streamlit` (Web UI)
- `plotly` (Visualization)
- `pandas` / `numpy` (Analytics)

## Usage

### 🚀 Web Application (Recommended)
The easiest way to explore all features (Simulation, AI, Validation).
```bash
streamlit run app_launcher.py
```
*Accessible at http://localhost:8501*

### 💻 Command Line Interface (CLI)

**1. Single Simulation Run**
Run a detailed simulation with default settings.
```bash
python -m src.main
```

**2. AI Optimization Mode**
Automatically find the best machine configuration.
```bash
python -m src.main --ai-optimize
```

**3. Generate Synthetic "Real" Data**
Create a test CSV to try the Validation mode.
```bash
python -m src.generate_real_data
```

## Project Structure
```
production_line_digital_twin/
├── app_launcher.py         # Entry point for Streamlit App
├── src/
│   ├── main.py             # CLI Entry point
│   ├── simulation.py       # Core SimPy Model (Machines, Logic, Failures)
│   ├── optimization.py     # AI Grid Search & Scenario Comparison
│   ├── analysis.py         # Metrics, Financials, Bottlenecks
│   ├── visualization.py    # Plotly Dashboards
│   ├── animation.py        # Real-time Visualization Logic
│   ├── generate_real_data.py # Synthetic Data Generator
│   └── config.py           # Global Configuration (Times, Costs, Machines)
├── data/
│   ├── results/            # Simulation Outputs (Metrics, CSVs)
│   └── raw/                # Real-world data for validation
└── README.md
```

## Configuration
Edit `src/config.py` to adjust:
- **Simulation**: `SIM_TIME`, `WARMUP_TIME`, `INTERARRIVAL_MEAN`.
- **Machines**: `MTBF`, `MTTR`, cost and processing times.
- **Economics**: Labor rates, energy costs, holding costs.

## Authors
Created for Advanced Agentic Coding - Digital Twin Project.
