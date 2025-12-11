# main.py — runs the simulation, analysis, and visualization
import sys
import os
from .simulation import run_simulation
from .analysis import (
    compute_throughput, compute_average_lead_time, 
    detect_bottleneck_simple, detect_bottleneck_advanced,
    compute_comprehensive_metrics, save_metrics, print_metrics_summary,
    calculate_financials, print_financial_report
)
from .visualization import (
    plot_machine_utilization, plot_throughput_time_series,
    plot_queue_lengths, plot_wip, plot_bottleneck_analysis,
    plot_waiting_times, create_gantt_chart, create_interactive_dashboard,
    plot_scenario_comparison
)
from .animation import (
    create_production_animation, create_static_flow_diagram,
    create_machine_state_timeline
)
from .optimization import compare_scenarios, generate_recommendations, print_recommendations
from . import config


def run_single_simulation():
    """Run a single simulation with comprehensive analysis and visualization"""
    print('='*80)
    print('PRODUCTION LINE DIGITAL TWIN - SINGLE RUN MODE')
    print('='*80)
    print(f'\nRunning simulation for {config.SIM_TIME} minutes...')
    
    # Run simulation
    df_results, df_mstats, df_queue, df_wip = run_simulation(
        sim_time=config.SIM_TIME, 
        verbose=False
    )
    
    # Save data to files
    print('\nSaving results to data/results/...')
    os.makedirs('data/results', exist_ok=True)
    save_metrics(
        df_results, df_mstats, 
        prefix='data/results/', 
        df_queue=df_queue, 
        df_wip=df_wip
    )
    
    # Compute comprehensive metrics
    metrics = compute_comprehensive_metrics(
        df_results, df_mstats, df_queue, df_wip, config.SIM_TIME
    )
    
    # Print metrics summary
    print_metrics_summary(metrics)
    
    # Advanced bottleneck detection
    df_bottleneck = detect_bottleneck_advanced(df_mstats, df_results, df_queue)
    
    print("\nBOTTLENECK ANALYSIS:")
    print("-" * 80)
    print(df_bottleneck.to_string(index=False))
    print(f"\nTop Bottleneck:", df_bottleneck.iloc[0]['machine'], 
          f"(Score: {df_bottleneck.iloc[0]['bottleneck_score']:.3f})")
    
    # Financial Analysis
    financials = calculate_financials(df_mstats, df_wip, config.SIM_TIME/60.0)
    print_financial_report(financials, metrics['total_completed'])
    
    # Create visualizations
    print("\nGenerating visualizations...")
    
    # Get machine names for Gantt chart
    machine_names = [m['name'] for m in config.MACHINES]
    
    # Individual plots (commented out by default, dashboard shows everything)
    # plot_machine_utilization(df_mstats, show=False, 
    #                         highlight_bottleneck=df_bottleneck.iloc[0]['machine'])
    # plot_queue_lengths(df_queue, show=False)
    # plot_wip(df_wip, show=False)
    # plot_bottleneck_analysis(df_bottleneck, show=False)
    # plot_waiting_times(df_results, show=False)
    # create_gantt_chart(df_results, machine_names, max_products=15, show=False)
    
    # Create and show interactive dashboard
    print("Creating interactive dashboard...")
    dashboard = create_interactive_dashboard(
        df_results, df_mstats, df_queue, df_wip, df_bottleneck
    )
    dashboard.show()
    
    # Also show Gantt chart separately
    print("Creating Gantt chart...")
    gantt = create_gantt_chart(df_results, machine_names, max_products=15, show=True)
    
    # Show production line animation
    print("Creating production line animation...")
    animation_fig = create_production_animation(df_results, df_queue, machine_names, max_time=120)
    animation_fig.show()
    
    print("\n" + "="*80)
    print("Simulation complete! Check data/results/ for CSV files.")
    print("="*80)


def run_optimization_mode():
    """Run multiple scenarios and provide optimization recommendations"""
    print('='*80)
    print('PRODUCTION LINE DIGITAL TWIN - OPTIMIZATION MODE')
    print('='*80)
    print('\nComparing optimization scenarios...')
    print('This may take a few minutes...\n')
    
    # Run scenario comparison
    comparison_df = compare_scenarios(num_replications=3)
    
    # Save comparison results
    os.makedirs('data/results', exist_ok=True)
    comparison_df.to_csv('data/results/scenario_comparison.csv', index=False)
    
    # Display comparison
    print("\n" + "="*80)
    print("SCENARIO COMPARISON RESULTS")
    print("="*80)
    print(comparison_df.to_string(index=False))
    
    # Generate and display recommendations
    recommendations = generate_recommendations(comparison_df)
    print_recommendations(recommendations)
    
    # Create comparison visualization
    print("\nGenerating comparison dashboard...")
    comparison_viz = plot_scenario_comparison(comparison_df, show=True)
    
    print("\n" + "="*80)
    print("Optimization analysis complete!")
    print("Results saved to: data/results/scenario_comparison.csv")
    print("="*80)


def run_ai_optimization_mode():
    """Run AI-powered grid search to find optimal configuration"""
    print('='*80)
    print('PRODUCTION LINE DIGITAL TWIN - AI OPTIMIZATION MODE')
    print('='*80)
    print('\nUsing Grid Search to find optimal machine configuration...')
    print('This will explore multiple configurations systematically.\n')
    
    from .optimization import grid_search_optimization, print_grid_search_summary
    
    # Get user constraints (or use defaults)
    target_throughput = 15.0  # items/hr
    max_cost = 300  # cost units
    
    print(f"Optimization Constraints:")
    print(f"  • Target Throughput: {target_throughput} items/hr")
    print(f"  • Max Implementation Cost: ${max_cost}")
    print(f"\nStarting optimization...\n")
    
    # Run grid search
    df_results, best_config = grid_search_optimization(
        target_throughput=target_throughput,
        max_cost=max_cost,
        capacity_ranges={
            'Cutting': (1, 3),
            'Drilling': (1, 3),
            'Assembly': (2, 4),
            'Painting': (1, 3)
        },
        num_replications=2,  # Fewer reps for speed
        verbose=True
    )
    
    # Save results
    os.makedirs('data/results', exist_ok=True)
    df_results.to_csv('data/results/ai_optimization_results.csv', index=False)
    
    # Print summary
    print_grid_search_summary(df_results, best_config)
    
    print("\n" + "="*80)
    print("AI Optimization complete!")
    print("Results saved to: data/results/ai_optimization_results.csv")
    print("="*80)


def print_usage():
    """Print usage instructions"""
    print("\nUsage:")
    print("  python -m src.main                 Run single simulation with dashboard")
    print("  python -m src.main --optimize      Run optimization scenario comparison")
    print("  python -m src.main --ai-optimize   Run AI grid search optimization")
    print("  python -m src.main --help          Show this help message")


def main():
    """Main entry point with command-line interface"""
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == '--optimize':
            run_optimization_mode()
        elif mode == '--ai-optimize':
            run_ai_optimization_mode()
        elif mode == '--help':
            print_usage()
        else:
            print(f"Unknown option: {mode}")
            print_usage()
    else:
        # Default: run single simulation
        run_single_simulation()


if __name__ == '__main__':
    main()
