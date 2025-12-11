"""
Optimization module for production line digital twin
Provides scenario generation, comparison, and recommendation capabilities
"""

import pandas as pd
import numpy as np
from .simulation import run_simulation
from .config import OPTIMIZATION_SCENARIOS, SIM_TIME


def run_scenario(scenario_name, scenario_config, sim_time=SIM_TIME, num_replications=5):
    """
    Run a specific scenario multiple times and return aggregated results
    
    Args:
        scenario_name: Name of the scenario
        scenario_config: Configuration dictionary with 'machines' and 'interarrival_mean'
        sim_time: Simulation time in minutes
        num_replications: Number of replications to run
    
    Returns:
        Dictionary with aggregated metrics
    """
    from .simulation import ProductionLineModel
    import simpy
    
    results_list = []
    mstats_list = []
    
    for rep in range(num_replications):
        env = simpy.Environment()
        model = ProductionLineModel(
            env, 
            scenario_config['machines'], 
            scenario_config['interarrival_mean']
        )
        env.run(until=sim_time)
        
        df_results = model.collect_results()
        df_mstats = model.machine_stats()
        
        results_list.append(df_results)
        mstats_list.append(df_mstats)
    
    # Aggregate metrics across replications
    throughputs = [len(df) / (sim_time / 60.0) for df in results_list]
    lead_times = [df['lead_time'].mean() if not df.empty else 0 for df in results_list]
    
    # Average utilizations per machine
    all_utils = {}
    for df_m in mstats_list:
        for _, row in df_m.iterrows():
            machine = row['machine']
            if machine not in all_utils:
                all_utils[machine] = []
            all_utils[machine].append(row['utilization'])
    
    avg_utils = {m: np.mean(utils) for m, utils in all_utils.items()}
    max_util_machine = max(avg_utils, key=avg_utils.get)
    max_util = avg_utils[max_util_machine]
    
    return {
        'scenario': scenario_name,
        'throughput_mean': np.mean(throughputs),
        'throughput_std': np.std(throughputs),
        'lead_time_mean': np.mean(lead_times),
        'lead_time_std': np.std(lead_times),
        'bottleneck_machine': max_util_machine,
        'bottleneck_utilization': max_util,
        'cost': scenario_config.get('cost', 0)
    }


def compare_scenarios(scenarios=None, sim_time=SIM_TIME, num_replications=3):
    """
    Compare multiple scenarios and return a DataFrame with results
    
    Args:
        scenarios: Dictionary of scenarios (default: OPTIMIZATION_SCENARIOS)
        sim_time: Simulation time in minutes
        num_replications: Number of replications per scenario
    
    Returns:
        DataFrame with comparison metrics
    """
    if scenarios is None:
        scenarios = OPTIMIZATION_SCENARIOS
    
    results = []
    for scenario_name, scenario_config in scenarios.items():
        print(f"Running scenario: {scenario_config['name']}...")
        metrics = run_scenario(scenario_name, scenario_config, sim_time, num_replications)
        results.append(metrics)
    
    df = pd.DataFrame(results)
    
    # Calculate improvement vs baseline
    baseline_throughput = df[df['scenario'] == 'baseline']['throughput_mean'].values[0]
    df['throughput_improvement_%'] = ((df['throughput_mean'] - baseline_throughput) / baseline_throughput * 100)
    
    baseline_lead_time = df[df['scenario'] == 'baseline']['lead_time_mean'].values[0]
    df['lead_time_reduction_%'] = ((baseline_lead_time - df['lead_time_mean']) / baseline_lead_time * 100)
    
    # Calculate cost-effectiveness (throughput improvement per unit cost)
    df['cost_effectiveness'] = df.apply(
        lambda row: row['throughput_improvement_%'] / row['cost'] if row['cost'] > 0 else 0,
        axis=1
    )
    
    return df


def generate_recommendations(comparison_df):
    """
    Generate optimization recommendations based on scenario comparison
    
    Args:
        comparison_df: DataFrame from compare_scenarios
    
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Remove baseline from consideration
    candidates = comparison_df[comparison_df['scenario'] != 'baseline'].copy()
    
    if candidates.empty:
        return [{"priority": "High", "recommendation": "No alternative scenarios to evaluate"}]
    
    # Best throughput improvement
    best_throughput = candidates.loc[candidates['throughput_improvement_%'].idxmax()]
    recommendations.append({
        'priority': 'High',
        'category': 'Maximum Throughput',
        'recommendation': f"For maximum throughput, implement '{best_throughput['scenario']}' configuration",
        'impact': f"+{best_throughput['throughput_improvement_%']:.1f}% throughput",
        'cost': f"{best_throughput['cost']} units",
        'bottleneck': f"Bottleneck: {best_throughput['bottleneck_machine']} ({best_throughput['bottleneck_utilization']:.1%})"
    })
    
    # Best cost-effectiveness
    best_roi = candidates.loc[candidates['cost_effectiveness'].idxmax()]
    recommendations.append({
        'priority': 'Medium',
        'category': 'Best ROI',
        'recommendation': f"For best return on investment, implement '{best_roi['scenario']}' configuration",
        'impact': f"+{best_roi['throughput_improvement_%']:.1f}% throughput at {best_roi['cost']} units cost",
        'cost': f"{best_roi['cost']} units",
        'roi': f"{best_roi['cost_effectiveness']:.2f} improvement per cost unit"
    })
    
    # Identify critical bottleneck
    baseline = comparison_df[comparison_df['scenario'] == 'baseline'].iloc[0]
    recommendations.append({
        'priority': 'High',
        'category': 'Bottleneck Alert',
        'recommendation': f"Current bottleneck is {baseline['bottleneck_machine']} at {baseline['bottleneck_utilization']:.1%} utilization",
        'impact': "This station limits overall system throughput",
        'suggestion': f"Consider adding capacity to {baseline['bottleneck_machine']}"
    })
    
    # Check for scenarios with significantly reduced lead time
    best_lead_time = candidates.loc[candidates['lead_time_reduction_%'].idxmax()]
    if best_lead_time['lead_time_reduction_%'] > 5:  # More than 5% improvement
        recommendations.append({
            'priority': 'Medium',
            'category': 'Lead Time Reduction',
            'recommendation': f"To reduce customer wait times, consider '{best_lead_time['scenario']}' configuration",
            'impact': f"-{best_lead_time['lead_time_reduction_%']:.1f}% lead time",
            'cost': f"{best_lead_time['cost']} units"
        })
    
    return recommendations


def print_recommendations(recommendations):
    """Pretty print recommendations"""
    print("\n" + "="*80)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("="*80)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n[{rec['priority']} Priority] {rec['category']}")
        print(f"  • {rec['recommendation']}")
        if 'impact' in rec:
            print(f"  • Impact: {rec['impact']}")
        if 'cost' in rec:
            print(f"  • Cost: {rec['cost']}")
        if 'roi' in rec:
            print(f"  • ROI: {rec['roi']}")
        if 'bottleneck' in rec:
            print(f"  • {rec['bottleneck']}")
        if 'suggestion' in rec:
            print(f"  • {rec['suggestion']}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("Running scenario comparisons...")
    comparison = compare_scenarios(num_replications=3)
    print("\n" + comparison.to_string(index=False))
    
    recommendations = generate_recommendations(comparison)
    print_recommendations(recommendations)
