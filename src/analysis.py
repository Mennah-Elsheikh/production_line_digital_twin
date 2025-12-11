# analysis.py — compute metrics and bottleneck detection
import pandas as pd
import numpy as np
from .config import (
    LABOR_RATE_PER_HR, ENERGY_KW_RATE, ENERGY_IDLE_KW, ENERGY_BUSY_KW,
    HOLDING_COST_PER_ITEM_HR, DOWNTIME_COST_PER_MIN
)


def compute_throughput(df_results, sim_time_minutes):
    # throughput: items per hour
    finished = len(df_results)
    hours = sim_time_minutes / 60.0
    return finished / hours if hours>0 else 0


def compute_average_lead_time(df_results):
    return df_results['lead_time'].mean() if not df_results.empty else None


def detect_bottleneck_simple(df_machine_stats):
    """Simple heuristic: highest utilization"""
    df = df_machine_stats.copy()
    df = df.sort_values('utilization', ascending=False)
    top = df.iloc[0]
    return top.to_dict()


def detect_bottleneck_advanced(df_machine_stats, df_results, df_queue):
    """
    Advanced bottleneck detection using multiple criteria:
    - Utilization: % time busy
    - Queue Length: Avg products waiting
    - Wait Time: Avg time spent waiting
    - Cycle Time: Avg time between consecutive outputs
    
    Returns a scored ranking of potential bottlenecks
    """
    bottleneck_scores = []
    
    # Pre-calculate cycle times per machine if possible
    cycle_times = {}
    if not df_results.empty:
        for machine in df_machine_stats['machine']:
            # Find finish times for this machine
            end_col = f'{machine}_end'
            if end_col in df_results.columns:
                # Sort by finish time
                finish_times = sorted(df_results[end_col].dropna())
                if len(finish_times) > 1:
                    # avg diff between finish times
                    diffs = np.diff(finish_times)
                    cycle_times[machine] = np.mean(diffs)
                else:
                    cycle_times[machine] = 0
            else:
                cycle_times[machine] = 0
    
    max_cycle_time = max(cycle_times.values()) if cycle_times else 1
    
    for _, machine in df_machine_stats.iterrows():
        machine_name = machine['machine']
        
        # Criterion 1: Utilization (higher is worse)
        utilization = machine['utilization']
        
        # Criterion 2: Average queue length
        queue_col = f'{machine_name}_queue'
        if not df_queue.empty and queue_col in df_queue.columns:
            avg_queue = df_queue[queue_col].mean()
        else:
            avg_queue = 0
        
        # Criterion 3: Average waiting time
        wait_col = f'{machine_name}_wait_time'
        if not df_results.empty and wait_col in df_results.columns:
            avg_wait = df_results[wait_col].mean()
        else:
            avg_wait = 0
            
        # Criterion 4: Cycle Time (normalized relative to slowest machine)
        # Slower cycle time = higher likelihood of being bottleneck
        c_time = cycle_times.get(machine_name, 0)
        norm_cycle = c_time / max_cycle_time if max_cycle_time > 0 else 0
        
        # Calculate composite bottleneck score (weighted average)
        # Weights: Util(40%), Queue(20%), Wait(20%), Cycle(20%)
        score = (
            0.4 * utilization +
            0.2 * (avg_queue / (avg_queue + 2)) +  # Normalized: assumes queue > 5 is bad
            0.2 * (avg_wait / (avg_wait + 10)) +   # Normalized: assumes wait > 10m is bad
            0.2 * norm_cycle
        )
        
        # Cap score at 1.0
        score = min(1.0, score)
        
        bottleneck_scores.append({
            'machine': machine_name,
            'bottleneck_score': score,
            'utilization': utilization,
            'avg_queue_length': avg_queue,
            'avg_wait_time_minutes': avg_wait,
            'cycle_time_minutes': c_time,
            'capacity': machine['capacity'],
            'processed': machine['processed']
        })
    
    df_bottleneck = pd.DataFrame(bottleneck_scores)
    if not df_bottleneck.empty:
        df_bottleneck = df_bottleneck.sort_values('bottleneck_score', ascending=False)
    
    return df_bottleneck


def compute_comprehensive_metrics(df_results, df_machine_stats, df_queue, df_wip, sim_time):
    """
    Compute comprehensive performance metrics
    
    Returns a dictionary with all key metrics
    """
    metrics = {}
    
    # Throughput metrics
    metrics['throughput_per_hour'] = compute_throughput(df_results, sim_time)
    metrics['total_completed'] = len(df_results)
    
    # Lead time metrics
    if not df_results.empty:
        metrics['avg_lead_time'] = df_results['lead_time'].mean()
        metrics['min_lead_time'] = df_results['lead_time'].min()
        metrics['max_lead_time'] = df_results['lead_time'].max()
        metrics['std_lead_time'] = df_results['lead_time'].std()
    else:
        metrics['avg_lead_time'] = None
        metrics['min_lead_time'] = None
        metrics['max_lead_time'] = None
        metrics['std_lead_time'] = None
    
    # Utilization metrics
    metrics['avg_utilization'] = df_machine_stats['utilization'].mean()
    metrics['min_utilization'] = df_machine_stats['utilization'].min()
    metrics['max_utilization'] = df_machine_stats['utilization'].max()
    
    # WIP metrics
    if not df_wip.empty:
        metrics['avg_wip'] = df_wip['wip'].mean()
        metrics['max_wip'] = df_wip['wip'].max()
    else:
        metrics['avg_wip'] = None
        metrics['max_wip'] = None
    
    # Queue metrics
    if not df_queue.empty:
        queue_cols = [col for col in df_queue.columns if col != 'time']
        if queue_cols:
            metrics['avg_total_queue'] = df_queue[queue_cols].sum(axis=1).mean()
    else:
        metrics['avg_total_queue'] = None
    
    return metrics


def save_metrics(df_results, df_machine_stats, prefix='', df_queue=None, df_wip=None):
    """Save all metrics to CSV files"""
    df_results.to_csv(prefix + 'results.csv', index=False)
    df_machine_stats.to_csv(prefix + 'machine_stats.csv', index=False)
    
    if df_queue is not None and not df_queue.empty:
        df_queue.to_csv(prefix + 'queue_data.csv', index=False)
    
    if df_wip is not None and not df_wip.empty:
        df_wip.to_csv(prefix + 'wip_data.csv', index=False)


def print_metrics_summary(metrics):
    """Pretty print metrics summary"""
    print("\n" + "="*60)
    print("PERFORMANCE METRICS SUMMARY")
    print("="*60)
    
    print(f"\nThroughput:")
    print(f"  • Items per hour: {metrics['throughput_per_hour']:.2f}")
    print(f"  • Total completed: {metrics['total_completed']}")
    
    if metrics['avg_lead_time'] is not None:
        print(f"\nLead Time:")
        print(f"  • Average: {metrics['avg_lead_time']:.2f} minutes")
        print(f"  • Range: {metrics['min_lead_time']:.2f} - {metrics['max_lead_time']:.2f} minutes")
        print(f"  • Std Dev: {metrics['std_lead_time']:.2f} minutes")
    
    print(f"\nMachine Utilization:")
    print(f"  • Average: {metrics['avg_utilization']:.1%}")
    print(f"  • Range: {metrics['min_utilization']:.1%} - {metrics['max_utilization']:.1%}")
    
    if metrics['avg_wip'] is not None:
        print(f"\nWork-In-Progress:")
        print(f"  • Average WIP: {metrics['avg_wip']:.1f} items")
        print(f"  • Maximum WIP: {metrics['max_wip']:.0f} items")
    
    if metrics['avg_total_queue'] is not None:
        print(f"\nQueue Metrics:")
        print(f"  • Average total queue length: {metrics['avg_total_queue']:.1f} items")
    
    print("="*60 + "\n")


def calculate_financials(df_mstats, df_wip, sim_time_hours):
    """
    Calculate comprehensive financial metrics based on simulation results.
    """
    metrics = {}
    
    # 1. Labor Cost (Total Capacity * Hours * Rate)
    total_capacity = df_mstats['capacity'].sum()
    metrics['labor_cost'] = total_capacity * sim_time_hours * LABOR_RATE_PER_HR
    
    # 2. Energy Cost
    # Calculate total busy time in hours
    total_busy_hours = df_mstats['busy_time'].sum() / 60.0
    total_downtime_hours = df_mstats['downtime'].sum() / 60.0
    
    # Total available machine hours
    total_machine_hours = total_capacity * sim_time_hours
    
    # Idle hours = Total - Busy - Downtime (assuming downtime is strictly off/repair)
    total_idle_hours = total_machine_hours - total_busy_hours - total_downtime_hours
    
    energy_busy = total_busy_hours * ENERGY_BUSY_KW * ENERGY_KW_RATE
    energy_idle = max(0, total_idle_hours) * ENERGY_IDLE_KW * ENERGY_KW_RATE
    metrics['energy_cost'] = energy_busy + energy_idle
    
    # 3. Downtime Cost
    total_downtime_min = df_mstats['downtime'].sum()
    metrics['downtime_cost'] = total_downtime_min * DOWNTIME_COST_PER_MIN
    
    # 4. WIP Holding Cost
    if not df_wip.empty:
        avg_wip = df_wip['wip'].mean()
    else:
        avg_wip = 0
        
    metrics['holding_cost'] = avg_wip * HOLDING_COST_PER_ITEM_HR * sim_time_hours
    
    # Total
    metrics['total_cost'] = (metrics['labor_cost'] + metrics['energy_cost'] + 
                             metrics['downtime_cost'] + metrics['holding_cost'])
                             
    return metrics

def print_financial_report(metrics, throughput):
    print("\n" + "="*60)
    print("FINANCIAL ANALYSIS (Estimated)")
    print("="*60)
    print(f"Total Operational Cost:  ${metrics['total_cost']:,.2f}")
    print(f"  - Labor Cost:          ${metrics['labor_cost']:,.2f} ({metrics['labor_cost']/metrics['total_cost']*100:.1f}%)")
    print(f"  - Energy Cost:         ${metrics['energy_cost']:,.2f} ({metrics['energy_cost']/metrics['total_cost']*100:.1f}%)")
    print(f"  - Downtime Cost:       ${metrics['downtime_cost']:,.2f} ({metrics['downtime_cost']/metrics['total_cost']*100:.1f}%)")
    print(f"  - WIP Holding Cost:    ${metrics['holding_cost']:,.2f} ({metrics['holding_cost']/metrics['total_cost']*100:.1f}%)")
    
    if throughput > 0:
        cpu = metrics['total_cost'] / throughput
        print(f"\nCost Per Unit Produced:  ${cpu:,.2f}")
    print("="*60 + "\n")


def compare_real_vs_sim(df_real, df_sim, sim_time):
    """
    Compare Real-world data vs Simulation results
    
    Args:
        df_real: DataFrame with real production logs
        df_sim: DataFrame with simulation results
        sim_time: Total time in minutes
        
    Returns:
        Dictionary of comparison metrics
    """
    metrics = {}
    
    # 1. Throughput Comparison
    th_real = len(df_real) / (sim_time / 60.0)
    th_sim = len(df_sim) / (sim_time / 60.0)
    
    metrics['throughput_real'] = th_real
    metrics['throughput_sim'] = th_sim
    metrics['throughput_error_%'] = ((th_sim - th_real) / th_real) * 100
    
    # 2. Lead Time Comparison
    lt_real = df_real['lead_time'].mean()
    lt_sim = df_sim['lead_time'].mean()
    
    metrics['lead_time_real'] = lt_real
    metrics['lead_time_sim'] = lt_sim
    metrics['lead_time_error_%'] = ((lt_sim - lt_real) / lt_real) * 100
    
    # 3. Validation Score (0-100%)
    # Simple accuracy score based on error margins
    th_accuracy = max(0, 100 - abs(metrics['throughput_error_%']))
    lt_accuracy = max(0, 100 - abs(metrics['lead_time_error_%']))
    metrics['validation_score'] = (th_accuracy + lt_accuracy) / 2
    
    return metrics
