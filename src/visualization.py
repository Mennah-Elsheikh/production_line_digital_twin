# visualization.py — plotting helpers
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def plot_machine_utilization(df_mstats, show=True, savepath=None, highlight_bottleneck=None):
    """
    Plot machine utilization with optional bottleneck highlighting
    
    Args:
        df_mstats: Machine statistics DataFrame
        show: Whether to display the plot
        savepath: Optional path to save the plot
        highlight_bottleneck: Optional machine name to highlight as bottleneck
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['red' if m == highlight_bottleneck else 'steelblue' 
              for m in df_mstats['machine']]
    
    ax.bar(df_mstats['machine'], df_mstats['utilization'], color=colors)
    ax.set_ylabel('Utilization (fraction)')
    ax.set_title('Machine Utilizations')
    ax.axhline(y=0.8, color='orange', linestyle='--', label='80% threshold')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    if savepath:
        fig.savefig(savepath)
    if show:
        plt.show()
    return fig


def plot_throughput_time_series(df_results, show=True):
    """Plot cumulative throughput over time"""
    if df_results.empty:
        return None
    df = df_results.sort_values('finished')
    df['cum_count'] = range(1, len(df)+1)
    fig = px.line(df, x='finished', y='cum_count', 
                  title='Cumulative Throughput vs Time',
                  labels={'finished': 'Time (minutes)', 'cum_count': 'Cumulative Items'})
    fig.update_traces(line_color='steelblue', line_width=2)
    if show:
        fig.show()
    return fig


def plot_queue_lengths(df_queue, show=True):
    """
    Plot queue lengths over time for all stations
    """
    if df_queue.empty:
        return None
    
    # Melt the dataframe to long format for plotly
    queue_cols = [col for col in df_queue.columns if col != 'time']
    df_long = df_queue.melt(id_vars=['time'], value_vars=queue_cols,
                             var_name='Station', value_name='Queue Length')
    
    # Clean up station names (remove _queue suffix)
    df_long['Station'] = df_long['Station'].str.replace('_queue', '')
    
    fig = px.line(df_long, x='time', y='Queue Length', color='Station',
                  title='Queue Lengths Over Time',
                  labels={'time': 'Time (minutes)'})
    fig.update_layout(hovermode='x unified')
    
    if show:
        fig.show()
    return fig


def plot_wip(df_wip, show=True):
    """
    Plot Work-In-Progress over time
    """
    if df_wip.empty:
        return None
    
    fig = px.area(df_wip, x='time', y='wip',
                  title='Work-In-Progress Over Time',
                  labels={'time': 'Time (minutes)', 'wip': 'WIP (items)'})
    fig.update_traces(fillcolor='lightblue', line_color='steelblue')
    
    if show:
        fig.show()
    return fig


def plot_bottleneck_analysis(df_bottleneck, show=True):
    """
    Visualize bottleneck analysis with scores
    """
    fig = go.Figure()
    
    # Add bars for bottleneck score
    fig.add_trace(go.Bar(
        x=df_bottleneck['machine'],
        y=df_bottleneck['bottleneck_score'],
        name='Bottleneck Score',
        marker_color='crimson',
        text=df_bottleneck['bottleneck_score'].round(3),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Bottleneck Analysis (Higher Score = More Critical)',
        xaxis_title='Machine',
        yaxis_title='Bottleneck Score',
        showlegend=True
    )
    
    if show:
        fig.show()
    return fig


def plot_waiting_times(df_results, show=True):
    """
    Plot average waiting times per station
    """
    if df_results.empty:
        return None
    
    # Extract wait time columns
    wait_cols = [col for col in df_results.columns if col.endswith('_wait_time')]
    
    if not wait_cols:
        return None
    
    wait_data = []
    for col in wait_cols:
        station = col.replace('_wait_time', '')
        avg_wait = df_results[col].mean()
        wait_data.append({'Station': station, 'Avg Wait Time': avg_wait})
    
    df_wait = pd.DataFrame(wait_data)
    
    fig = px.bar(df_wait, x='Station', y='Avg Wait Time',
                 title='Average Waiting Time per Station',
                 labels={'Avg Wait Time': 'Average Wait Time (minutes)'},
                 color='Avg Wait Time',
                 color_continuous_scale='Reds')
    
    if show:
        fig.show()
    return fig


def create_gantt_chart(df_results, machine_names, max_products=20, show=True):
    """
    Create a Gantt chart showing machine schedules
    
    Args:
        df_results: Results DataFrame with timing information
        machine_names: List of machine names
        max_products: Maximum number of products to show (for clarity)
        show: Whether to display the chart
    """
    if df_results.empty:
        return None
    
    # Limit to first N products for readability
    df_sample = df_results.head(max_products)
    
    # Base time for better visualization (e.g. today 8:00 AM)
    base_time = pd.Timestamp.now().normalize() + pd.Timedelta(hours=8)
    
    gantt_data = []
    for _, product in df_sample.iterrows():
        product_id = product['id']
        for machine in machine_names:
            start_col = f'{machine}_start'
            end_col = f'{machine}_end'
            
            if start_col in product and end_col in product:
                start_val = product[start_col]
                end_val = product[end_col]
                
                if pd.notna(start_val) and pd.notna(end_val):
                    # Convert minutes to datetime objects
                    start_dt = base_time + pd.Timedelta(minutes=start_val)
                    end_dt = base_time + pd.Timedelta(minutes=end_val)
                    
                    gantt_data.append({
                        'Product': product_id,
                        'Machine': machine,
                        'Start': start_dt,
                        'Finish': end_dt,
                        'Duration Minutes': end_val - start_val
                    })
    
    if not gantt_data:
        return None
    
    df_gantt = pd.DataFrame(gantt_data)
    
    fig = px.timeline(df_gantt, x_start='Start', x_end='Finish', y='Product', 
                      color='Machine',
                      title=f'Machine Schedule (First {max_products} Products)',
                      hover_data=['Duration Minutes'])
    
    fig.update_yaxes(autorange="reversed")  # Products from top to bottom
    fig.update_xaxes(title='Time')
    
    if show:
        fig.show()
    return fig


def create_interactive_dashboard(df_results, df_mstats, df_queue, df_wip, df_bottleneck):
    """
    Create a comprehensive interactive dashboard with all key metrics
    
    Returns a plotly figure with multiple subplots
    """
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('Machine Utilization', 'Bottleneck Scores',
                        'Queue Lengths Over Time', 'WIP Over Time',
                        'Cumulative Throughput', 'Average Waiting Times'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'scatter'}, {'type': 'scatter'}],
               [{'type': 'scatter'}, {'type': 'bar'}]],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # 1. Machine Utilization
    fig.add_trace(
        go.Bar(x=df_mstats['machine'], y=df_mstats['utilization'],
               name='Utilization', marker_color='steelblue',
               showlegend=False),
        row=1, col=1
    )
    
    # 2. Bottleneck Scores
    fig.add_trace(
        go.Bar(x=df_bottleneck['machine'], y=df_bottleneck['bottleneck_score'],
               name='Bottleneck', marker_color='crimson',
               showlegend=False),
        row=1, col=2
    )
    
    # 3. Queue Lengths
    if not df_queue.empty:
        queue_cols = [col for col in df_queue.columns if col != 'time']
        for col in queue_cols:
            station_name = col.replace('_queue', '')
            fig.add_trace(
                go.Scatter(x=df_queue['time'], y=df_queue[col],
                          mode='lines', name=station_name),
                row=2, col=1
            )
    
    # 4. WIP
    if not df_wip.empty:
        fig.add_trace(
            go.Scatter(x=df_wip['time'], y=df_wip['wip'],
                      mode='lines', fill='tozeroy', name='WIP',
                      line_color='steelblue', showlegend=False),
            row=2, col=2
        )
    
    # 5. Cumulative Throughput
    if not df_results.empty:
        df_sorted = df_results.sort_values('finished')
        cum_count = list(range(1, len(df_sorted) + 1))
        fig.add_trace(
            go.Scatter(x=df_sorted['finished'], y=cum_count,
                      mode='lines', name='Throughput',
                      line_color='green', showlegend=False),
            row=3, col=1
        )
    
    # 6. Waiting Times
    if not df_results.empty:
        wait_cols = [col for col in df_results.columns if col.endswith('_wait_time')]
        if wait_cols:
            wait_data = []
            for col in wait_cols:
                station = col.replace('_wait_time', '')
                avg_wait = df_results[col].mean()
                wait_data.append({'station': station, 'wait': avg_wait})
            df_wait = pd.DataFrame(wait_data)
            
            fig.add_trace(
                go.Bar(x=df_wait['station'], y=df_wait['wait'],
                      marker_color='orange', showlegend=False),
                row=3, col=2
            )
    
    # Update axes labels
    fig.update_xaxes(title_text="Machine", row=1, col=1)
    fig.update_xaxes(title_text="Machine", row=1, col=2)
    fig.update_xaxes(title_text="Time (minutes)", row=2, col=1)
    fig.update_xaxes(title_text="Time (minutes)", row=2, col=2)
    fig.update_xaxes(title_text="Time (minutes)", row=3, col=1)
    fig.update_xaxes(title_text="Station", row=3, col=2)
    
    fig.update_yaxes(title_text="Utilization", row=1, col=1)
    fig.update_yaxes(title_text="Score", row=1, col=2)
    fig.update_yaxes(title_text="Queue Length", row=2, col=1)
    fig.update_yaxes(title_text="WIP", row=2, col=2)
    fig.update_yaxes(title_text="Items", row=3, col=1)
    fig.update_yaxes(title_text="Minutes", row=3, col=2)
    
    fig.update_layout(
        title_text="Production Line Performance Dashboard",
        height=1200,
        showlegend=True
    )
    
    return fig


def plot_scenario_comparison(comparison_df, show=True):
    """
    Create visualizations comparing different scenarios
    
    Args:
        comparison_df: DataFrame from optimization.compare_scenarios()
        show: Whether to display plots
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Throughput Comparison', 'Lead Time Comparison',
                        'Cost vs Throughput Improvement', 'Cost Effectiveness'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'scatter'}, {'type': 'bar'}]]
    )
    
    # 1. Throughput
    fig.add_trace(
        go.Bar(x=comparison_df['scenario'], y=comparison_df['throughput_mean'],
               name='Throughput', marker_color='steelblue',
               error_y=dict(type='data', array=comparison_df['throughput_std']),
               showlegend=False),
        row=1, col=1
    )
    
    # 2. Lead Time
    fig.add_trace(
        go.Bar(x=comparison_df['scenario'], y=comparison_df['lead_time_mean'],
               name='Lead Time', marker_color='coral',
               error_y=dict(type='data', array=comparison_df['lead_time_std']),
               showlegend=False),
        row=1, col=2
    )
    
    # 3. Cost vs Improvement (scatter)
    fig.add_trace(
        go.Scatter(x=comparison_df['implementation_cost'], y=comparison_df['throughput_improvement_%'],
                   mode='markers+text', text=comparison_df['scenario'],
                   textposition='top center', marker=dict(size=12, color='green'),
                   showlegend=False),
        row=2, col=1
    )
    
    # 4. Cost Effectiveness
    fig.add_trace(
        go.Bar(x=comparison_df['scenario'], y=comparison_df['cost_effectiveness'],
               name='ROI', marker_color='purple', showlegend=False),
        row=2, col=2
    )
    
    fig.update_xaxes(title_text="Implementation Cost", row=2, col=1)
    fig.update_yaxes(title_text="Throughput Improvement (%)", row=2, col=1)
    
    # Update axes
    fig.update_xaxes(title_text="Scenario", row=1, col=1)
    fig.update_xaxes(title_text="Scenario", row=1, col=2)
    fig.update_xaxes(title_text="Cost (units)", row=2, col=1)
    fig.update_xaxes(title_text="Scenario", row=2, col=2)
    
    fig.update_yaxes(title_text="Items/hour", row=1, col=1)
    fig.update_yaxes(title_text="Minutes", row=1, col=2)
    fig.update_yaxes(title_text="Improvement %", row=2, col=1)
    fig.update_yaxes(title_text="Improvement/Cost", row=2, col=2)
    
    fig.update_layout(
        title_text="Scenario Comparison Dashboard",
        height=800,
        showlegend=False
    )
    
    if show:
        fig.show()
    
    return fig


def plot_real_vs_sim(df_real, df_sim):
    """
    Plot comparison between Real and Simulated data
    
    Args:
        df_real: Real data DataFrame
        df_sim: Simulation data DataFrame
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Throughput Comparison (Boxplot)", "Lead Time Distribution", 
            "Cumulative Production", "Lead Time Scatter"
        )
    )
    
    # 1. Throughput Comparison (Boxplot derived from hourly rates if possible, simplified here)
    # Actually, let's use Lead Time Boxplot for robust comparison
    fig.add_trace(go.Box(y=df_real['lead_time'], name='Real', marker_color='blue'), row=1, col=1)
    fig.add_trace(go.Box(y=df_sim['lead_time'], name='Simulated', marker_color='orange'), row=1, col=1)
    
    # 2. Lead Time Distribution
    fig.add_trace(go.Histogram(x=df_real['lead_time'], name='Real', opacity=0.75, marker_color='blue'), row=1, col=2)
    fig.add_trace(go.Histogram(x=df_sim['lead_time'], name='Simulated', opacity=0.75, marker_color='orange'), row=1, col=2)
    fig.update_layout(barmode='overlay')
    
    # 3. Cumulative Production
    # Sort both
    if 'finished' in df_real.columns and 'finished' in df_sim.columns:
        real_sorted = df_real.sort_values('finished')
        sim_sorted = df_sim.sort_values('finished')
        
        fig.add_trace(go.Scatter(x=real_sorted['finished'], y=np.arange(len(real_sorted)), 
                                name='Real Production', line=dict(color='blue')), row=2, col=1)
        fig.add_trace(go.Scatter(x=sim_sorted['finished'], y=np.arange(len(sim_sorted)), 
                                name='Simulated Production', line=dict(color='orange', dash='dash')), row=2, col=1)
    
    # 4. Lead Time Scatter
    fig.add_trace(go.Scatter(x=df_real.index, y=df_real['lead_time'], name='Real', mode='markers', marker_color='blue', opacity=0.5), row=2, col=2)
    fig.add_trace(go.Scatter(x=df_sim.index, y=df_sim['lead_time'], name='Simulated', mode='markers', marker_color='orange', opacity=0.5), row=2, col=2)
    
    fig.update_layout(title="Digital Twin Validation: Real vs. Simulated", height=800)
    
    # Update axes
    fig.update_yaxes(title_text="Lead Time (min)", row=1, col=1)
    fig.update_xaxes(title_text="Lead Time (min)", row=1, col=2)
    fig.update_xaxes(title_text="Time (minutes)", row=2, col=1)
    fig.update_yaxes(title_text="Cumulative Production", row=2, col=1)
    
    return fig
