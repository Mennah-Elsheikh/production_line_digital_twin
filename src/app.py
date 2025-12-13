"""
Streamlit Web Application for Production Line Digital Twin
Run with: streamlit run src/app.py
"""

import streamlit as st
import pandas as pd
import simpy
from src.simulation import ProductionLineModel
from src.analysis import (
    compute_comprehensive_metrics, detect_bottleneck_advanced,
    calculate_financials, print_metrics_summary, compare_real_vs_sim
)
from src.visualization import (
    create_interactive_dashboard, create_gantt_chart, plot_scenario_comparison,
    plot_real_vs_sim
)
from src.animation import (
    create_production_animation, create_static_flow_diagram,
    create_machine_state_timeline
)
from src.optimization import compare_scenarios
from src.config import MACHINES, SIM_TIME, WARMUP_TIME, INTERARRIVAL_MEAN

st.set_page_config(
    page_title="Production Line Digital Twin",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def run_simulation_model(machines_config, sim_time, warmup_time, interarrival_mean):
    """Run simulation and return results"""
    env = simpy.Environment()
    model = ProductionLineModel(env, machines_config, interarrival_mean, warmup_time=warmup_time)
    
    with st.spinner(f'Running simulation for {sim_time} minutes...'):
        env.run(until=sim_time)
    
    df_results = model.collect_results()
    df_mstats = model.machine_stats()
    df_queue = model.get_queue_data()
    df_wip = model.get_wip_data()
    
    return df_results, df_mstats, df_queue, df_wip

def main():
    st.markdown('<h1 class="main-header">🏭 Production Line Digital Twin</h1>', unsafe_allow_html=True)
    
    # Sidebar Configuration
    st.sidebar.title("⚙️ Configuration")
    
    mode = st.sidebar.radio(
        "Select Mode",
        ["Single Simulation", "Optimization Comparison", "Digital Twin Validation"],
        help="Choose between running a single simulation, comparing multiple scenarios, or validating against real data"
    )
    
    st.sidebar.markdown("---")
    
    # Simulation Parameters
    st.sidebar.subheader("Simulation Parameters")
    sim_time = st.sidebar.number_input(
        "Simulation Time (minutes)",
        min_value=60,
        max_value=1440,
        value=SIM_TIME,
        step=60,
        help="Total simulation runtime"
    )
    
    warmup_time = st.sidebar.number_input(
        "Warm-up Period (minutes)",
        min_value=0,
        max_value=120,
        value=WARMUP_TIME,
        step=10,
        help="Data collected during this period is discarded for steady-state analysis"
    )
    
    interarrival_mean = st.sidebar.number_input(
        "Mean Interarrival Time (minutes)",
        min_value=0.5,
        max_value=10.0,
        value=INTERARRIVAL_MEAN,
        step=0.5,
        help="Average time between product arrivals"
    )
    
    st.sidebar.markdown("---")
    
    # Machine Configuration
    st.sidebar.subheader("Machine Capacities")
    machines_config = []
    
    for machine in MACHINES:
        capacity = st.sidebar.number_input(
            f"{machine['name']} Capacity",
            min_value=1,
            max_value=5,
            value=machine['capacity'],
            key=f"capacity_{machine['name']}"
        )
        machines_config.append({
            **machine,
            'capacity': capacity
        })
    
    st.sidebar.markdown("---")
    run_button = st.sidebar.button("🚀 Run Simulation", type="primary")
    
    # Main Content Area
    if mode == "Single Simulation":
        st.header("📊 Single Simulation Dashboard")
        
        if run_button:
            # Run simulation
            df_results, df_mstats, df_queue, df_wip = run_simulation_model(
                machines_config, sim_time, warmup_time, interarrival_mean
            )
            
            # Store in session state
            st.session_state['df_results'] = df_results
            st.session_state['df_mstats'] = df_mstats
            st.session_state['df_queue'] = df_queue
            st.session_state['df_wip'] = df_wip
            st.success("✅ Simulation complete!")
        
        # Display results if available
        if 'df_results' in st.session_state:
            df_results = st.session_state['df_results']
            df_mstats = st.session_state['df_mstats']
            df_queue = st.session_state['df_queue']
            df_wip = st.session_state['df_wip']
            
            # Compute metrics
            metrics = compute_comprehensive_metrics(
                df_results, df_mstats, df_queue, df_wip, sim_time
            )
            
            # Key Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Throughput",
                    f"{metrics['throughput_per_hour']:.2f} items/hr",
                    f"{metrics['total_completed']} completed"
                )
            
            with col2:
                avg_lt = metrics.get('avg_lead_time', 0) or 0
                std_lt = metrics.get('std_lead_time', 0) or 0
                st.metric(
                    "Avg Lead Time",
                    f"{avg_lt:.1f} min",
                    f"±{std_lt:.1f} min"
                )
            
            with col3:
                st.metric(
                    "Avg Utilization",
                    f"{metrics['avg_utilization']:.1%}",
                    f"{metrics['min_utilization']:.1%} - {metrics['max_utilization']:.1%}"
                )
            
            with col4:
                st.metric(
                    "Avg WIP",
                    f"{metrics.get('avg_wip', 0):.1f} items",
                    f"Max: {metrics.get('max_wip', 0):.0f}"
                )
            
            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Dashboard", "🎬 Animation", "🔍 Bottleneck Analysis", 
                "💰 Financial Report", "📋 Data Tables"
            ])
            
            with tab1:
                st.subheader("Interactive Dashboard")
                df_bottleneck = detect_bottleneck_advanced(df_mstats, df_results, df_queue)
                fig_dashboard = create_interactive_dashboard(
                    df_results, df_mstats, df_queue, df_wip, df_bottleneck
                )
                st.plotly_chart(fig_dashboard, use_container_width=True)
                
                st.subheader("Machine Schedule (Gantt Chart)")
                machine_names = [m['name'] for m in machines_config]
                fig_gantt = create_gantt_chart(df_results, machine_names, max_products=20, show=False)
                st.plotly_chart(fig_gantt, use_container_width=True)
            
            with tab2:
                st.subheader("Production Line Animation")
                st.write("Watch products flow through the production line in real-time!")
                
                # Animation controls
                col1, col2 = st.columns(2)
                with col1:
                    max_time_anim = st.slider(
                        "Animation Duration (minutes)",
                        min_value=30,
                        max_value=int(sim_time),
                        value=min(120, int(sim_time)),
                        step=30
                    )
                
                # Production flow animation
                fig_animation = create_production_animation(
                    df_results, df_queue, machine_names, max_time=max_time_anim
                )
                st.plotly_chart(fig_animation, use_container_width=True)
                
                st.subheader("Machine Activity Timeline")
                fig_timeline = create_machine_state_timeline(
                    df_results, machine_names, max_products=30
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                st.subheader("Production Flow Diagram")
                fig_flow = create_static_flow_diagram(machine_names)
                st.plotly_chart(fig_flow, use_container_width=True)
            
            with tab3:
                st.subheader("Advanced Bottleneck Detection")
                df_bottleneck = detect_bottleneck_advanced(df_mstats, df_results, df_queue)
                
                st.dataframe(
                    df_bottleneck.style.background_gradient(subset=['bottleneck_score'], cmap='Reds'),
                    use_container_width=True
                )
                
                top_bottleneck = df_bottleneck.iloc[0]
                st.error(f"🚨 **Primary Bottleneck:** {top_bottleneck['machine']} "
                        f"(Score: {top_bottleneck['bottleneck_score']:.3f}, "
                        f"Utilization: {top_bottleneck['utilization']:.1%})")
            
            with tab4:
                st.subheader("Financial Analysis")
                financials = calculate_financials(df_mstats, df_wip, sim_time/60.0)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Operational Cost", f"${financials['total_cost']:,.2f}")
                    st.metric("Cost Per Unit", f"${financials['total_cost']/metrics['total_completed']:,.2f}")
                
                with col2:
                    st.write("**Cost Breakdown:**")
                    cost_data = pd.DataFrame({
                        'Category': ['Labor', 'Energy', 'Downtime', 'WIP Holding'],
                        'Cost': [
                            financials['labor_cost'],
                            financials['energy_cost'],
                            financials['downtime_cost'],
                            financials['holding_cost']
                        ]
                    })
                    st.bar_chart(cost_data.set_index('Category'))
            
            with tab5:
                st.subheader("Machine Statistics")
                st.dataframe(df_mstats, use_container_width=True)
                
                st.subheader("Product Results (Sample)")
                st.dataframe(df_results.head(20), use_container_width=True)
                
                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download Results CSV",
                        df_results.to_csv(index=False),
                        "results.csv",
                        "text/csv"
                    )
                with col2:
                    st.download_button(
                        "📥 Download Machine Stats CSV",
                        df_mstats.to_csv(index=False),
                        "machine_stats.csv",
                        "text/csv"
                    )
    
    elif mode == "Digital Twin Validation":
        st.header("🔄 Digital Twin Validation")
        st.info("Compare simulation results against real-world production data.")
        
        # File uploader
        uploaded_file = st.file_uploader("Upload Real Production Log (CSV)", type="csv")
        
        # Fallback to generated data if available
        if uploaded_file is not None:
             # User uploaded a file
             df_real = pd.read_csv(uploaded_file)
             st.session_state['df_real'] = df_real
             st.success(f"Uploaded {len(df_real)} records.")
        
        elif st.button("Load 'Real' Data from data/raw/"):
             # User clicked load button
             try:
                 df_real = pd.read_csv('data/raw/real_production_log.csv')
                 st.session_state['df_real'] = df_real
                 st.success(f"Loaded {len(df_real)} synthetic real records.")
             except FileNotFoundError:
                 st.error("No real data file found at data/raw/real_production_log.csv")
        
        # Check if data exists in session state
        if 'df_real' in st.session_state:
            df_real = st.session_state['df_real']
            st.write(f"Using dataset with {len(df_real)} records.")
            
            if run_button:
                # Run Simulation
                df_results, df_mstats, df_queue, df_wip = run_simulation_model(
                    machines_config, sim_time, warmup_time, interarrival_mean
                )
                
                # Compare
                metrics = compare_real_vs_sim(df_real, df_results, sim_time)
                
                # Display Validation Score
                score = metrics['validation_score']
                color = "green" if score > 80 else "orange" if score > 50 else "red"
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
                    <h2>Digital Twin Accuracy</h2>
                    <h1 style="color: {color}; font-size: 60px;">{score:.1f}%</h1>
                </div>
                """, unsafe_allow_html=True)
                
                # Comparison Metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Real Throughput", f"{metrics['throughput_real']:.2f} items/hr")
                    st.metric("Sim Throughput", f"{metrics['throughput_sim']:.2f} items/hr", 
                              f"{metrics['throughput_error_%']:.1f}% error")
                
                with col2:
                    st.metric("Real Avg Lead Time", f"{metrics['lead_time_real']:.1f} min")
                    st.metric("Sim Avg Lead Time", f"{metrics['lead_time_sim']:.1f} min",
                              f"{metrics['lead_time_error_%']:.1f}% error")
                
                # Visual Comparison
                st.subheader("Visual Comparison")
                fig_comp = plot_real_vs_sim(df_real, df_results)
                st.plotly_chart(fig_comp, use_container_width=True)
                
    else:  # Optimization Mode
        st.header("🔬 Optimization Scenario Comparison")
        
        num_replications = st.slider(
            "Number of Replications per Scenario",
            min_value=1,
            max_value=10,
            value=3,
            help="More replications = more accurate but slower"
        )
        
        if run_button:
            with st.spinner("Running optimization scenarios... This may take a few minutes."):
                comparison_df = compare_scenarios(num_replications=num_replications)
                st.session_state['comparison_df'] = comparison_df
            st.success("✅ Optimization complete!")
        
        if 'comparison_df' in st.session_state:
            comparison_df = st.session_state['comparison_df']
            
            st.subheader("Scenario Comparison Table")
            st.dataframe(
                comparison_df.style.background_gradient(subset=['throughput_improvement_%'], cmap='Greens'),
                use_container_width=True
            )
            
            st.subheader("Visual Comparison")
            fig_comparison = plot_scenario_comparison(comparison_df, show=False)
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            st.subheader("🎯 Recommendations")
            
            # Best throughput
            best_throughput = comparison_df[comparison_df['scenario'] != 'baseline'].loc[
                comparison_df['throughput_improvement_%'].idxmax()
            ]
            st.success(f"**Maximum Throughput:** {best_throughput['scenario']} "
                      f"(+{best_throughput['throughput_improvement_%']:.1f}% throughput, "
                      f"${best_throughput['implementation_cost']} CapEx)")
            
            # Best ROI
            best_roi = comparison_df[comparison_df['scenario'] != 'baseline'].loc[
                comparison_df['cost_effectiveness'].idxmax()
            ]
            st.info(f"**Best ROI:** {best_roi['scenario']} "
                   f"({best_roi['cost_effectiveness']:.2f} improvement per cost unit)")
            
            # Lowest OpEx
            best_opex = comparison_df.loc[comparison_df['operational_cost'].idxmin()]
            st.warning(f"**Lowest Operational Cost:** {best_opex['scenario']} "
                      f"(${best_opex['operational_cost']:,.2f} OpEx)")
            
            # Download
            st.download_button(
                "📥 Download Comparison CSV",
                comparison_df.to_csv(index=False),
                "scenario_comparison.csv",
                "text/csv"
            )

if __name__ == "__main__":
    main()
