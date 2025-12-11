# Production Line Digital Twin

A comprehensive discrete event simulation of a multi-stage manufacturing production line using **SimPy**, with advanced analytics, bottleneck identification, and optimization recommendations.

## Features

✨ **Discrete Event Simulation**
- Multi-stage production line (Cutting → Drilling → Assembly → Painting)
- Resource allocation and queue management
- Exponential/deterministic processing times
- Work-in-Progress (WIP) tracking

📊 **Advanced Analytics**
- Multi-criteria bottleneck detection
- Throughput and lead time analysis
- Queue length and waiting time metrics
- Machine utilization tracking
- Comprehensive performance metrics

🎯 **Optimization Engine**
- Multiple scenario comparison
- Cost-benefit analysis
- Automated optimization recommendations
- ROI calculations

📈 **Interactive Visualizations**
- Comprehensive performance dashboard
- Queue length tracking over time
- WIP visualization
- Gantt charts for machine scheduling
- Bottleneck identification charts
- Scenario comparison dashboards

## Installation

### 1. Clone the Repository
```bash
cd "d:\College Projects\production_line_digital_twin"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `simpy>=4.0.1` - Discrete event simulation
- `pandas>=1.5` - Data analysis
- `numpy>=1.23` - Numerical computing
- `matplotlib>=3.6` - Static plotting
- `plotly>=5.13.1` - Interactive visualizations
- `scipy>=1.9.3` - Scientific computing

## Usage

### Basic Simulation

Run a single simulation with comprehensive analysis and interactive dashboard:

```bash
python -m src.main
```

**Output:**
- Console metrics summary (throughput, lead time, utilization, WIP)
- Bottleneck analysis with multi-criteria scoring
- Interactive dashboard (opens in browser)
- Gantt chart showing machine schedules
- CSV files in `data/results/`:
  - `results.csv` - Individual product data
  - `machine_stats.csv` - Machine performance
  - `queue_data.csv` - Queue length snapshots
  - `wip_data.csv` - Work-in-progress over time

### Optimization Mode

Compare multiple configuration scenarios with recommendations:

```bash
python -m src.main --optimize
```

**Output:**
- Scenario comparison table
- Optimization recommendations with priority levels
- Cost-effectiveness analysis
- Scenario comparison dashboard
- `data/results/scenario_comparison.csv`

### Help

```bash
python -m src.main --help
```

## Configuration

Edit `src/config.py` to customize simulation parameters:

```python
# Simulation settings
SIM_TIME = 8 * 60  # 8 hours in minutes
INTERARRIVAL_MEAN = 2.0  # Mean time between arrivals (minutes)
SEED = 42  # Random seed for reproducibility

# Machine definitions
MACHINES = [
    {"name": "Cutting", "capacity": 1, "proc_mean": 3.0},
    {"name": "Drilling", "capacity": 1, "proc_mean": 4.5},
    {"name": "Assembly", "capacity": 2, "proc_mean": 6.0},
    {"name": "Painting", "capacity": 1, "proc_mean": 2.5},
]

# Processing time distribution
PROC_DISTRIBUTION = "exp"  # Options: 'exp', 'det'
```

## Project Structure

```
production_line_digital_twin/
├── src/
│   ├── config.py           # Configuration parameters
│   ├── simulation.py       # SimPy simulation model
│   ├── analysis.py         # Performance metrics & bottleneck detection
│   ├── visualization.py    # Interactive dashboards & charts
│   ├── optimization.py     # Scenario comparison & recommendations
│   └── main.py             # Main entry point with CLI
├── data/
│   ├── raw/                # Raw data (if any)
│   └── results/            # Simulation outputs (CSV files)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Key Metrics

### Performance Metrics
- **Throughput**: Items produced per hour
- **Lead Time**: Total time from arrival to completion
- **Cycle Time**: Processing time variation
- **WIP**: Work-in-progress (items in system)

### Machine Metrics
- **Utilization**: Fraction of time machine is busy
- **Queue Length**: Average items waiting
- **Waiting Time**: Average time products wait in queue
- **Processed Count**: Total items processed

### Bottleneck Scoring
Multi-criteria composite score based on:
- **40%** Machine utilization
- **30%** Average queue length
- **30%** Average waiting time

Higher score = more critical bottleneck

## Optimization Scenarios

Pre-configured scenarios in `config.py`:

1. **Baseline** - Current configuration (no additional cost)
2. **Add Drilling Machine** - +1 Drilling capacity (cost: 100 units)
3. **Add Assembly Machine** - +1 Assembly capacity (cost: 120 units)
4. **Balanced Line** - Increase all capacities (cost: 350 units)

**Customize** by adding scenarios to `OPTIMIZATION_SCENARIOS` dict.

## Interpreting Results

### Dashboard Panels
1. **Machine Utilization** - Identify overworked machines (>80%)
2. **Bottleneck Scores** - Multi-criteria bottleneck ranking
3. **Queue Lengths** - Track queue buildup patterns
4. **WIP Over Time** - System congestion indicator
5. **Cumulative Throughput** - Production rate visualization
6. **Waiting Times** - Identify delay hotspots

### Optimization Recommendations
The system provides prioritized recommendations:
- **High Priority** - Critical bottlenecks and max throughput options
- **Medium Priority** - Cost-effective improvements and lead time reductions

Each recommendation includes:
- Impact on throughput/lead time
- Implementation cost
- ROI calculation

## Example Output

```
============================================================
PERFORMANCE METRICS SUMMARY
============================================================

Throughput:
  • Items per hour: 19.88
  • Total completed: 159

Lead Time:
  • Average: 52.34 minutes
  • Range: 15.23 - 145.67 minutes
  • Std Dev: 28.91 minutes

Machine Utilization:
  • Average: 82.4%
  • Range: 36.4% - 99.3%

Work-In-Progress:
  • Average WIP: 32.5 items
  • Maximum WIP: 78 items

============================================================

BOTTLENECK ANALYSIS:
Machine     Bottleneck Score  Utilization  Avg Queue  Avg Wait Time
Cutting              0.728        0.993        8.34          15.23
Drilling             0.701        0.975        6.12          12.45
Assembly             0.625        0.920        3.45           8.67
Painting             0.401        0.364        0.23           0.89

Top Bottleneck: Cutting (Score: 0.728)
```

## Advanced Use Cases

### Custom Scenario Analysis

```python
from src.optimization import run_scenario, generate_recommendations

# Define custom scenario
custom_scenario = {
    'name': 'High Speed Line',
    'machines': [
        {"name": "Cutting", "capacity": 2, "proc_mean": 2.0},
        {"name": "Drilling", "capacity": 2, "proc_mean": 3.0},
        {"name": "Assembly", "capacity": 3, "proc_mean": 4.0},
        {"name": "Painting", "capacity": 2, "proc_mean": 1.5},
    ],
    'interarrival_mean': 1.5,
    'cost': 500
}

# Run analysis
metrics = run_scenario('custom', custom_scenario, num_replications=5)
print(metrics)
```

### Export for Further Analysis

All data is saved as CSV in `data/results/`:
- Import into Excel, Tableau, or Power BI
- Perform statistical analysis in R or Python
- Create custom visualizations

## Troubleshooting

### No Products Finished
- **Cause**: Simulation time too short or arrival rate too low
- **Solution**: Increase `SIM_TIME` or decrease `INTERARRIVAL_MEAN`

### Dashboard Not Opening
- **Cause**: Browser blocking or Plotly issue
- **Solution**: Check console output, try different browser

### Import Errors
- **Cause**: Missing dependencies
- **Solution**: Run `pip install -r requirements.txt`

## Future Enhancements

Potential additions:
- Machine breakdowns and maintenance
- Setup times and batch processing
- Priority scheduling algorithms
- Real-time monitoring dashboard
- Machine learning for demand forecasting
- Multi-product variants

## Authors

Created for discrete event simulation and production optimization analysis.

## License

MIT License - Feel free to use and modify for your projects.

## Acknowledgments

- **SimPy** - Discrete event simulation framework
- **Plotly** - Interactive visualization library
- **Pandas** - Data manipulation and analysis
