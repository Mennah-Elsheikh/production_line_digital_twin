# analysis.py — compute metrics and bottleneck detection
import pandas as pd
import numpy as np


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
    - Machine utilization
    - Average queue length
    - Average waiting time
    
    Returns a scored ranking of potential bottlenecks
    """
    bottleneck_scores = []
    
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
        
        # Calculate composite bottleneck score (weighted average)
        # Normalize criteria to 0-1 scale
        # Higher score = more likely to be bottleneck
        score = (
            0.4 * utilization +  # 40% weight on utilization
            0.3 * (avg_queue / (avg_queue + 1)) +  # 30% weight on queue (normalized)
            0.3 * (avg_wait / (avg_wait + 1))  # 30% weight on waiting time (normalized)
        )
        
        bottleneck_scores.append({
            'machine': machine_name,
            'bottleneck_score': score,
            'utilization': utilization,
            'avg_queue_length': avg_queue,
            'avg_wait_time_minutes': avg_wait,
            'capacity': machine['capacity'],
            'processed': machine['processed']
        })
    
    df_bottleneck = pd.DataFrame(bottleneck_scores)
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
