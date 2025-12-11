"""
Animation module for production line visualization
Creates real-time animated view of production flow
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np


def create_production_animation(df_results, df_queue, machine_names, max_time=None):
    """
    Create animated visualization of production line
    
    Shows:
    - Products flowing through stations
    - Queue lengths changing over time
    - Machine states (idle/busy/broken)
    
    Args:
        df_results: Product completion data
        df_queue: Queue snapshot data over time
        machine_names: List of machine names in order
        max_time: Maximum time to animate (None = all)
    
    Returns:
        Plotly figure with animation
    """
    
    if df_queue.empty:
        # Create simple static view if no queue data
        return create_static_flow_diagram(machine_names)
    
    # Determine time range
    if max_time is None:
        max_time = df_queue['time'].max()
    
    df_queue_filtered = df_queue[df_queue['time'] <= max_time].copy()
    
    # Create frames for animation
    frames = []
    time_points = sorted(df_queue_filtered['time'].unique())
    
    for t in time_points:
        frame_data = df_queue_filtered[df_queue_filtered['time'] == t]
        
        if frame_data.empty:
            continue
        
        # Extract queue lengths for each machine
        queue_lengths = []
        for machine in machine_names:
            col_name = f'{machine}_queue'
            if col_name in frame_data.columns:
                queue_lengths.append(frame_data[col_name].values[0])
            else:
                queue_lengths.append(0)
        
        # Create visualization data for this frame
        y_positions = list(range(len(machine_names)))
        
        # Create bars for queue lengths
        trace_queues = go.Bar(
            x=queue_lengths,
            y=machine_names,
            orientation='h',
            name='Queue Length',
            marker=dict(color='rgba(255, 140, 0, 0.6)'),
            text=queue_lengths,
            textposition='auto',
        )
        
        # Create machine status indicators (simplified - show as points)
        machine_x = [ql + 2 for ql in queue_lengths]  # Position machines after queues
        
        trace_machines = go.Scatter(
            x=machine_x,
            y=machine_names,
            mode='markers+text',
            name='Machines',
            marker=dict(
                size=30,
                color='steelblue',
                symbol='square',
                line=dict(width=2, color='darkblue')
            ),
            text=['⚙️'] * len(machine_names),
            textfont=dict(size=20),
        )
        
        frames.append(go.Frame(
            data=[trace_queues, trace_machines],
            name=str(t),
            layout=go.Layout(
                title_text=f"Production Line at t={t:.1f} min"
            )
        ))
    
    # Initial frame (t=0 or first available)
    if frames:
        initial_data = frames[0].data
    else:
        # Fallback if no frames
        initial_data = [
            go.Bar(x=[0]*len(machine_names), y=machine_names, orientation='h')
        ]
    
    # Create figure
    fig = go.Figure(
        data=initial_data,
        frames=frames,
        layout=go.Layout(
            title="🏭 Production Line Animation",
            xaxis=dict(
                title="Queue Length + Processing",
                range=[0, max(df_queue_filtered[[col for col in df_queue_filtered.columns if 'queue' in col]].max()) + 10]
            ),
            yaxis=dict(title="Station"),
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': '▶ Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 500, 'redraw': True},
                            'fromcurrent': True,
                            'mode': 'immediate',
                            'transition': {'duration': 300}
                        }]
                    },
                    {
                        'label': '⏸ Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ]
            }],
            sliders=[{
                'active': 0,
                'steps': [
                    {
                        'args': [[f.name], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }],
                        'label': f"{float(f.name):.1f}",
                        'method': 'animate'
                    }
                    for f in frames
                ],
                'x': 0.1,
                'len': 0.9,
                'xanchor': 'left',
                'y': 0,
                'yanchor': 'top'
            }],
            height=800,
            showlegend=True
        )
    )
    
    return fig


def create_static_flow_diagram(machine_names):
    """
    Create a static flow diagram showing the production line layout
    
    Args:
        machine_names: List of machine names
    
    Returns:
        Plotly figure
    """
    
    fig = go.Figure()
    
    num_machines = len(machine_names)
    x_positions = list(range(num_machines))
    
    # Add machines as nodes
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=[0] * num_machines,
        mode='markers+text',
        marker=dict(size=50, color='steelblue', symbol='square'),
        text=machine_names,
        textposition='top center',
        textfont=dict(size=14, color='black'),
        name='Machines',
        showlegend=False
    ))
    
    # Add arrows between machines
    for i in range(num_machines - 1):
        fig.add_annotation(
            x=x_positions[i+1],
            y=0,
            ax=x_positions[i],
            ay=0,
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor='gray'
        )
    
    fig.update_layout(
        title="Production Line Flow",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 1]),
        height=500,
        showlegend=False
    )
    
    return fig


def create_machine_state_timeline(df_results, machine_names, max_products=50):
    """
    Create a timeline showing machine states over time
    
    Args:
        df_results: Product results with timestamps
        machine_names: List of machines
        max_products: Maximum products to display
    
    Returns:
        Plotly figure
    """
    
    if df_results.empty:
        return go.Figure()
    
    df_sample = df_results.head(max_products)
    
    fig = go.Figure()
    
    colors = ['royalblue', 'crimson', 'gold', 'limegreen', 'purple']
    
    for idx, machine in enumerate(machine_names):
        start_col = f'{machine}_start'
        end_col = f'{machine}_end'
        
        if start_col in df_sample.columns and end_col in df_sample.columns:
            for i, row in df_sample.iterrows():
                if pd.notna(row[start_col]) and pd.notna(row[end_col]):
                    fig.add_trace(go.Scatter(
                        x=[row[start_col], row[end_col]],
                        y=[machine, machine],
                        mode='lines',
                        line=dict(width=5, color=colors[idx % len(colors)]),
                        name=machine if i == 0 else None,
                        showlegend=(i == 0),
                        hovertemplate=f"Product {row['id']}<br>Start: {row[start_col]:.1f}<br>End: {row[end_col]:.1f}<extra></extra>"
                    ))
    
    fig.update_layout(
        title="Machine Activity Timeline",
        xaxis_title="Time (minutes)",
        yaxis_title="Machine",
        height=600,
        hovermode='closest'
    )
    
    return fig
