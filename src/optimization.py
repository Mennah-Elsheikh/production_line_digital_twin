"""
Optimization module for production line digital twin
Provides scenario generation, comparison, and recommendation capabilities
"""

import pandas as pd
import numpy as np
from .simulation import run_simulation
from .config import OPTIMIZATION_SCENARIOS, SIM_TIME
from .analysis import calculate_financials


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
    wip_list = []
    
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
        df_wip = model.get_wip_data()
        
        results_list.append(df_results)
        mstats_list.append(df_mstats)
        wip_list.append(df_wip)
    
    # Aggregate metrics across replications
    throughputs = [len(df) / (sim_time / 60.0) for df in results_list]
    lead_times = [df['lead_time'].mean() if not df.empty else 0 for df in results_list]
    
    # Calculate average operational cost across replications
    opex_costs = []
    for df_m, df_w in zip(mstats_list, wip_list):
        fin = calculate_financials(df_m, df_w, sim_time/60.0)
        opex_costs.append(fin['total_cost'])
        
    avg_opex = np.mean(opex_costs)
    
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
        'implementation_cost': scenario_config.get('cost', 0),
        'operational_cost': avg_opex
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
    
    # Calculate cost-effectiveness (throughput improvement per unit implementation cost)
    df['cost_effectiveness'] = df.apply(
        lambda row: row['throughput_improvement_%'] / row['implementation_cost'] if row['implementation_cost'] > 0 else 0,
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
        'cost': f"{best_throughput['implementation_cost']} units (CapEx)",
        'bottleneck': f"Bottleneck: {best_throughput['bottleneck_machine']} ({best_throughput['bottleneck_utilization']:.1%})"
    })
    
    # Best cost-effectiveness (ROI on CapEx)
    best_roi = candidates.loc[candidates['cost_effectiveness'].idxmax()]
    recommendations.append({
        'priority': 'Medium',
        'category': 'Best ROI',
        'recommendation': f"For best return on investment, implement '{best_roi['scenario']}' configuration",
        'impact': f"+{best_roi['throughput_improvement_%']:.1f}% throughput at {best_roi['implementation_cost']} units cost",
        'cost': f"{best_roi['implementation_cost']} units",
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
            'cost': f"{best_lead_time['implementation_cost']} units"
        })

    # Lowest Operational Cost
    best_opex = comparison_df.loc[comparison_df['operational_cost'].idxmin()]
    baseline_opex = comparison_df[comparison_df['scenario'] == 'baseline']['operational_cost'].values[0]
    
    if best_opex['scenario'] != 'baseline' and best_opex['operational_cost'] < baseline_opex:
        savings = baseline_opex - best_opex['operational_cost']
        recommendations.append({
            'priority': 'Medium',
            'category': 'Lowest Operational Cost',
            'recommendation': f"To minimize daily OpEx, choose '{best_opex['scenario']}'",
            'impact': f"Save ${savings:,.2f} per run",
            'cost': f"OpEx: ${best_opex['operational_cost']:,.2f}"
        })
    elif best_opex['scenario'] == 'baseline':
         recommendations.append({
            'priority': 'Low',
            'category': 'Operational Cost',
            'recommendation': "Baseline configuration has the lowest operational cost",
            'impact': "No OpEx savings from changes",
            'cost': f"OpEx: ${best_opex['operational_cost']:,.2f}"
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


def grid_search_optimization(
    target_throughput=None,
    max_cost=None,
    capacity_ranges=None,
    sim_time=SIM_TIME,
    num_replications=3,
    verbose=True
):
    """
    AI-Powered Grid Search to find optimal machine configuration
    
    Args:
        target_throughput: Minimum acceptable throughput (items/hr)
        max_cost: Maximum acceptable implementation cost
        capacity_ranges: Dict mapping machine names to (min, max) capacity ranges
        sim_time: Simulation time
        num_replications: Number of simulation runs per configuration
        verbose: Print progress
    
    Returns:
        DataFrame with all evaluated configurations and best config dict
    """
    from .config import MACHINES, INTERARRIVAL_MEAN
    import itertools
    
    if capacity_ranges is None:
        # Default: allow 1-3 capacity for each machine
        capacity_ranges = {m['name']: (1, 3) for m in MACHINES}
    
    # Generate all possible configurations (Cartesian product)
    machine_names = [m['name'] for m in MACHINES]
    capacity_options = [
        range(capacity_ranges.get(name, (1, 3))[0], 
              capacity_ranges.get(name, (1, 3))[1] + 1)
        for name in machine_names
    ]
    
    all_configs = list(itertools.product(*capacity_options))
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"AI GRID SEARCH OPTIMIZATION")
        print(f"{'='*80}")
        print(f"Exploring {len(all_configs)} configurations...")
        print(f"Target Throughput: {target_throughput or 'None'} items/hr")
        print(f"Max Cost Constraint: {max_cost or 'None'} units")
        print(f"{'='*80}\n")
    
    results = []
    
    for idx, config_capacities in enumerate(all_configs):
        # Build machine configuration
        machines_config = []
        total_capacity = 0
        
        for i, machine in enumerate(MACHINES):
            capacity = config_capacities[i]
            total_capacity += capacity
            machines_config.append({
                **machine,
                'capacity': capacity
            })
        
        # Estimate implementation cost (assume cost = 100 per additional capacity)
        baseline_capacity = sum(m['capacity'] for m in MACHINES)
        added_capacity = total_capacity - baseline_capacity
        impl_cost = max(0, added_capacity * 100)
        
        # Skip if exceeds max cost
        if max_cost is not None and impl_cost > max_cost:
            continue
        
        # Run simulation
        if verbose and idx % 10 == 0:
            print(f"Testing config {idx+1}/{len(all_configs)}: {dict(zip(machine_names, config_capacities))}")
        
        scenario_config = {
            'machines': machines_config,
            'interarrival_mean': INTERARRIVAL_MEAN,
            'cost': impl_cost
        }
        
        metrics = run_scenario(
            f"config_{idx}",
            scenario_config,
            sim_time=sim_time,
            num_replications=num_replications
        )
        
        # Add configuration details
        for i, name in enumerate(machine_names):
            metrics[f'{name}_capacity'] = config_capacities[i]
        
        metrics['total_capacity'] = total_capacity
        metrics['config_id'] = idx
        
        results.append(metrics)
    
    df_results = pd.DataFrame(results)
    
    # Filter by constraints
    valid_configs = df_results.copy()
    
    if target_throughput is not None:
        valid_configs = valid_configs[valid_configs['throughput_mean'] >= target_throughput]
    
    if max_cost is not None:
        valid_configs = valid_configs[valid_configs['implementation_cost'] <= max_cost]
    
    if valid_configs.empty:
        if verbose:
            print("\n⚠️ WARNING: No configurations meet the constraints!")
            print("Showing all results instead...\n")
        valid_configs = df_results
    
    # Find best configuration (minimize cost, maximize throughput)
    # Score = throughput / (1 + cost)
    # Add score to valid_configs first
    valid_configs['score'] = valid_configs['throughput_mean'] / (1 + valid_configs['implementation_cost'])
    
    # Also add score to full results for API analysis/sorting
    df_results['score'] = df_results['throughput_mean'] / (1 + df_results['implementation_cost'])
    
    best_config = valid_configs.loc[valid_configs['score'].idxmax()]
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"OPTIMIZATION COMPLETE")
        print(f"{'='*80}")
        print(f"Evaluated: {len(df_results)} configurations")
        print(f"Valid (meeting constraints): {len(valid_configs)} configurations")
        print(f"\n🏆 BEST CONFIGURATION FOUND:")
        print(f"{'='*80}")
        
        for name in machine_names:
            print(f"  {name}: {int(best_config[f'{name}_capacity'])} units")
        
        print(f"\nPerformance:")
        print(f"  Throughput: {best_config['throughput_mean']:.2f} items/hr (±{best_config['throughput_std']:.2f})")
        print(f"  Lead Time: {best_config['lead_time_mean']:.2f} min")
        print(f"  Implementation Cost: ${best_config['implementation_cost']:.0f}")
        print(f"  Bottleneck: {best_config['bottleneck_machine']} ({best_config['bottleneck_utilization']:.1%})")
        print(f"  Optimization Score: {best_config['score']:.3f}")
        print(f"{'='*80}\n")
    
    return df_results, best_config


def print_grid_search_summary(df_results, best_config):
    """Print summary of grid search results"""
    
    # Ensure score column exists
    if 'score' not in df_results.columns:
        df_results['score'] = df_results['throughput_mean'] / (1 + df_results['implementation_cost'])
    
    print("\nTop 5 Configurations:")
    print("="*80)
    
    top_5 = df_results.nlargest(5, 'score')[
        ['scenario', 'throughput_mean', 'lead_time_mean', 
         'implementation_cost', 'bottleneck_utilization', 'score']
    ]
    print(top_5.to_string(index=False))
    print("="*80)


if __name__ == "__main__":
    print("Running scenario comparisons...")
    comparison = compare_scenarios(num_replications=3)
    print("\n" + comparison.to_string(index=False))
    
    recommendations = generate_recommendations(comparison)
    print_recommendations(recommendations)
