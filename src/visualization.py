# visualization.py — plotting helpers
import matplotlib.pyplot as plt
import plotly.express as px


def plot_machine_utilization(df_mstats, show=True, savepath=None):
    fig, ax = plt.subplots()
    ax.bar(df_mstats['machine'], df_mstats['utilization'])
    ax.set_ylabel('Utilization (fraction)')
    ax.set_title('Machine Utilizations')
    if savepath:
        fig.savefig(savepath)
    if show:
        plt.show()
    return fig


def plot_throughput_time_series(df_results, show=True):
    # cumulative throughput over time
    if df_results.empty:
        return None
    df = df_results.sort_values('finished')
    df['cum_count'] = range(1, len(df)+1)
    fig = px.line(df, x='finished', y='cum_count', title='Cumulative Throughput vs Time')
    if show:
        fig.show()
    return fig