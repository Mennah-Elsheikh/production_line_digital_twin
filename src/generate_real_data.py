"""
Generate synthetic 'real' data for Digital Twin validation.
Runs simulation with perturbed parameters to mimic real-world variance.
"""
import simpy
import pandas as pd
import random
import os
from src.simulation import ProductionLineModel
from src.config import MACHINES, SIM_TIME, INTERARRIVAL_MEAN

def generate_real_data():
    print("Generating synthetic 'Real-World' data...")
    
    # Perturb parameters to simulate reality gap
    real_machines = []
    for m in MACHINES:
        # 10% variance in processing time
        perturbed_mean = m['proc_mean'] * random.uniform(0.9, 1.2)
        # Higher failure rate in reality
        perturbed_mtbf = m['MTBF'] * 0.8
        
        real_machines.append({
            **m,
            'proc_mean': perturbed_mean,
            'MTBF': perturbed_mtbf
        })
    
    # Run simulation
    env = simpy.Environment()
    # Add some variability to arrival process
    real_interarrival = INTERARRIVAL_MEAN * 1.05
    
    model = ProductionLineModel(env, real_machines, real_interarrival)
    env.run(until=SIM_TIME)
    
    df_results = model.collect_results()
    
    # Add some noise to timestamps (measurement error)
    if not df_results.empty:
        df_results['lead_time'] = df_results['lead_time'] + [random.normalvariate(0, 2) for _ in range(len(df_results))]
    
    # Save
    os.makedirs('data/raw', exist_ok=True)
    output_path = 'data/raw/real_production_log.csv'
    df_results.to_csv(output_path, index=False)
    print(f"Generated {len(df_results)} records.")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    generate_real_data()
