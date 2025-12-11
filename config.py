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