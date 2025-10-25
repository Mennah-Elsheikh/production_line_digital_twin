# main.py — runs the simulation, analysis, and visualization
from simulation import run_simulation
from analysis import compute_throughput, compute_average_lead_time, detect_bottleneck, save_metrics
from visualization import plot_machine_utilization, plot_throughput_time_series
import config


def main():
    print('Running simulation for', config.SIM_TIME, 'minutes')
    df_results, df_mstats = run_simulation(sim_time=config.SIM_TIME, verbose=False)

    throughput = compute_throughput(df_results, config.SIM_TIME)
    avg_lead = compute_average_lead_time(df_results)
    bottleneck = detect_bottleneck(df_mstats)

    print(f'Throughput (items/hour): {throughput:.2f}')
    print(f'Average lead time (minutes): {avg_lead:.2f}' if avg_lead is not None else 'No finished items')
    print('Bottleneck candidate:', bottleneck)

    save_metrics(df_results, df_mstats)

    plot_machine_utilization(df_mstats, show=True)
    plot_throughput_time_series(df_results, show=True)

if __name__ == '__main__':
    main()