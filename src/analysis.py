# analysis.py — compute metrics and bottleneck detection
import pandas as pd


def compute_throughput(df_results, sim_time_minutes):
    # throughput: items per hour
    finished = len(df_results)
    hours = sim_time_minutes / 60.0
    return finished / hours if hours>0 else 0


def compute_average_lead_time(df_results):
    return df_results['lead_time'].mean() if not df_results.empty else None


def detect_bottleneck(df_machine_stats):
    # simple heuristic: highest utilization
    df = df_machine_stats.copy()
    df = df.sort_values('utilization', ascending=False)
    top = df.iloc[0]
    return top.to_dict()


def save_metrics(df_results, df_machine_stats, prefix=''):
    df_results.to_csv(prefix + 'results.csv', index=False)
    df_machine_stats.to_csv(prefix + 'machine_stats.csv', index=False)