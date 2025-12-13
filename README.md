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
## 🌟 Features

### 1. Modern Web Dashboard (The "Twin")
*   **Real-time Monitoring:** Throughput, Utilization, WIP tracking.
*   **Interactive Visualizations:** dynamic charts and bottleneck analysis.
*   **AI Optimization:** 'Optimize' mode to auto-tune machine parameters.
*   **Tech Stack:** HTML5/JS Frontend + FastAPI Backend.

### 2. Streamlit Data Science Lab (The "Brain")
*   **Deep Simulation Control:** Fine-tune simulation parameters (seeds, run times).
*   **Statistical Analysis:** Histograms, lead time distribution, confidence intervals.
*   **Validation:** Compare digital twin results against real-world datasets.
*   **Tech Stack:** Streamlit + SimPy + Pandas + Matplotlib.

---

## 🚀 Quick Start

### Local Installation
```bash
# 1. Clone repo
git clone https://github.com/Mennah-Elsheikh/production_line_digital_twin.git
cd production_line_digital_twin

# 2. Install dependencies
pip install -r requirements-local.txt

# 3. Run Everything!
# Terminal 1 (API):
uvicorn api.index:app --reload

# Terminal 2 (Web Frontend):
python -m http.server 8080 --directory public

# Terminal 3 (Streamlit):
streamlit run app_launcher.py
```

### 🌐 Live Demos
| Platform | Feature | URL |
|----------|---------|-----|
| **Vercel** | Web Dashboard | [Live Demo](https://production-line-digital-twin-g2o9.vercel.app/) |
| **Streamlit Cloud** | Simulation Lab | [Live App](https://digital-twin-line.streamlit.app/) |

---

## 📂 Project Structure

*   `src/`: Core simulation logic (SimPy models, Optimization engine).
*   `public/`: HTML/CSS/JS for the Web Dashboard.
*   `api/`: FastAPI backend (Serving the Web Dashboard).
*   `app_launcher.py`: Entry point for Streamlit.
*   `requirements-local.txt`: All dependencies for local dev.
*   `requirements.txt`: Dependencies for Streamlit Cloud.
*   `api/requirements.txt`: Minimal dependencies for Vercel.
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
