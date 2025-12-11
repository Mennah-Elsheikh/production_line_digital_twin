# config.py — central configuration for the production line


SEED = 42
SIM_TIME = 8 * 60 # simulate 8 hours (minutes)
WARMUP_TIME = 60 # Warm-up period in minutes
INTERARRIVAL_MEAN = 2.0 # mean minutes between new parts


# Machines definition: (capacity, mean_processing_time)
# capacity = number of parallel identical machines
MACHINES =  [
    {"name": "Cutting", "capacity": 1, "proc_mean": 3.0, "MTBF": 300, "MTTR": 30},
    {"name": "Drilling", "capacity": 1, "proc_mean": 4.5, "MTBF": 400, "MTTR": 40},
    {"name": "Assembly", "capacity": 2, "proc_mean": 6.0, "MTBF": 600, "MTTR": 60},
    {"name": "Painting", "capacity": 1, "proc_mean": 2.5, "MTBF": 300, "MTTR": 20},
]
# MTBF: Mean Time Between Failures (minutes)
# MTTR: Mean Time To Repair (minutes)



# Whether service times are deterministic or exponential
PROC_DISTRIBUTION = "exp" # options: 'exp', 'det'


# Output paths
RESULTS_CSV = "results.csv"
STATS_CSV = "machine_stats.csv"

# Economic Parameters (Cost Modeling)
LABOR_RATE_PER_HR = 20.0        # Rate for machine operator
ENERGY_KW_RATE = 0.15           # Cost per kWh
ENERGY_IDLE_KW = 0.5            # kW power when idle
ENERGY_BUSY_KW = 2.0            # kW power when processing
HOLDING_COST_PER_ITEM_HR = 5.0  # WIP holding cost
DOWNTIME_COST_PER_MIN = 10.0    # Cost of lost production/maintenance


# Optimization Scenarios
OPTIMIZATION_SCENARIOS = {
    'baseline': {
        'name': 'Baseline',
        'machines': MACHINES,
        'interarrival_mean': INTERARRIVAL_MEAN,
        'cost': 0  # relative cost
    },
    'add_drilling': {
        'name': 'Add Drilling Machine',
        'machines': [
            {"name": "Cutting", "capacity": 1, "proc_mean": 3.0},
            {"name": "Drilling", "capacity": 2, "proc_mean": 4.5},  # +1 capacity
            {"name": "Assembly", "capacity": 2, "proc_mean": 6.0},
            {"name": "Painting", "capacity": 1, "proc_mean": 2.5},
        ],
        'interarrival_mean': INTERARRIVAL_MEAN,
        'cost': 100  # relative cost units
    },
    'add_assembly': {
        'name': 'Add Assembly Machine',
        'machines': [
            {"name": "Cutting", "capacity": 1, "proc_mean": 3.0},
            {"name": "Drilling", "capacity": 1, "proc_mean": 4.5},
            {"name": "Assembly", "capacity": 3, "proc_mean": 6.0},  # +1 capacity
            {"name": "Painting", "capacity": 1, "proc_mean": 2.5},
        ],
        'interarrival_mean': INTERARRIVAL_MEAN,
        'cost': 120  # relative cost units
    },
    'balanced': {
        'name': 'Balanced Line',
        'machines': [
            {"name": "Cutting", "capacity": 2, "proc_mean": 3.0},
            {"name": "Drilling", "capacity": 2, "proc_mean": 4.5},
            {"name": "Assembly", "capacity": 3, "proc_mean": 6.0},
            {"name": "Painting", "capacity": 2, "proc_mean": 2.5},
        ],
        'interarrival_mean': INTERARRIVAL_MEAN,
        'cost': 350  # relative cost units
    }
}
