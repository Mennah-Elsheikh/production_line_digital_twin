# config.py — central configuration for the production line


SEED = 42
SIM_TIME = 8 * 60 # simulate 8 hours (minutes)
INTERARRIVAL_MEAN = 2.0 # mean minutes between new parts


# Machines definition: (capacity, mean_processing_time)
# capacity = number of parallel identical machines
MACHINES =  [
{"name": "Cutting", "capacity": 1, "proc_mean": 3.0},
{"name": "Drilling", "capacity": 1, "proc_mean": 4.5},
{"name": "Assembly", "capacity": 2, "proc_mean": 6.0},
{"name": "Painting", "capacity": 1, "proc_mean": 2.5},
]


# Whether service times are deterministic or exponential
PROC_DISTRIBUTION = "exp" # options: 'exp', 'det'


# Output paths
RESULTS_CSV = "results.csv"
STATS_CSV = "machine_stats.csv"


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
