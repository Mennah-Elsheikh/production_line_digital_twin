"""
FastAPI Backend for Production Line Digital Twin
Serverless deployment on Vercel
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import simpy
import numpy as np
import pandas as pd
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import ProductionLineModel
from src.analysis import compute_comprehensive_metrics, detect_bottleneck_advanced, calculate_financials
from src.config import MACHINES, SIM_TIME, INTERARRIVAL_MEAN, WARMUP_TIME

app = FastAPI(title="Production Line Digital Twin API")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulationConfig(BaseModel):
    sim_time: int = SIM_TIME
    interarrival_mean: float = INTERARRIVAL_MEAN
    warmup_time: float = WARMUP_TIME
    machines: list = None


@app.get("/")
def root():
    """Serve the frontend HTML"""
    from fastapi.responses import FileResponse
    import os
    html_path = os.path.join(os.path.dirname(__file__), '..', 'public', 'index.html')
    return FileResponse(html_path)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "digital-twin-api"}


@app.post("/api/simulate")
def run_simulation(config: SimulationConfig):
    """
    Run a production line simulation with given parameters
    """
    try:
        # Use default machines if not provided
        machines_config = config.machines if config.machines else MACHINES
        
        # Create simulation environment
        env = simpy.Environment()
        model = ProductionLineModel(
            env, 
            machines_config, 
            config.interarrival_mean,
            warmup_time=config.warmup_time
        )
        
        # Run simulation
        env.run(until=config.sim_time)
        
        # Collect results
        df_results = model.collect_results()
        df_mstats = model.machine_stats()
        df_queue = model.get_queue_data()
        df_wip = model.get_wip_data()
        
        # Calculate metrics
        metrics = compute_comprehensive_metrics(
            df_results, df_mstats, df_queue, df_wip, config.sim_time
        )
        
        # Detect bottlenecks
        df_bottleneck = detect_bottleneck_advanced(df_mstats, df_results, df_queue)
        
        # Prepare time-series data (downsampled for performance)
        # Queue over time
        queue_data = []
        if not df_queue.empty:
            # Resample to ~100 points max
            df_q_resampled = df_queue.iloc[::max(1, len(df_queue)//100)]
            for _, row in df_q_resampled.iterrows():
                queue_data.append({
                    "time": float(row['time']),
                    "value": float(row[[c for c in df_queue.columns if 'queue' in c]].sum())
                })
                
        # WIP over time
        wip_data = []
        if not df_wip.empty:
            df_w_resampled = df_wip.iloc[::max(1, len(df_wip)//100)]
            for _, row in df_w_resampled.iterrows():
                wip_data.append({
                    "time": float(row['time']),
                    "value": float(row['wip'])
                })

        # Cumulative Production over time
        production_data = []
        if not df_results.empty:
            # Sort by end time
            df_finished = df_results.sort_values('finished')
            # Resample? Or just take points
            # Let's take every Nth item to keep it light
            step = max(1, len(df_finished) // 100)
            count = 0
            for i in range(0, len(df_finished), step):
                row = df_finished.iloc[i]
                count = i + 1 # approximate cumulative count
                production_data.append({
                    "time": float(row['finished']),
                    "value": int(count)
                })
            # Add final point
            production_data.append({
                "time": float(df_finished.iloc[-1]['finished']),
                "value": int(len(df_finished))
            })

        # Lead Time Histogram
        lead_time_hist = {"labels": [], "data": []}
        if not df_results.empty and 'lead_time' in df_results.columns:
            # Create 10 bins
            hist, bin_edges = np.histogram(df_results['lead_time'], bins=10)
            lead_time_hist["labels"] = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(hist))]
            lead_time_hist["data"] = [int(x) for x in hist]

        # Machine Status Breakdown (Simulated estimates since we don't have full state logs in this simplified model)
        # We have utilization (busy). We can infer Idle = 1 - Busy. 
        # For a more advanced "Blocked", we'd need detailed logs, but we can stick to Busy vs Idle for now or approximate.
        machine_status = []
        for _, m in df_mstats.iterrows():
            busy = m['utilization']
            idle = max(0, 1.0 - busy)
            machine_status.append({
                "machine": m['machine'],
                "busy": float(round(busy * 100, 1)),
                "idle": float(round(idle * 100, 1))
            })

        # Financial Analysis
        financial_data = calculate_financials(df_mstats, df_wip, config.sim_time / 60.0)
        
        # Gantt Chart Data (Machine Schedule)
        gantt_data = []
        if not df_results.empty:
            # Take first 30 products for visualization
            df_gantt = df_results.head(30)
            for _, product in df_gantt.iterrows():
                product_id = product['id']
                for m in df_mstats['machine']:
                    start_col = f'{m}_start'
                    end_col = f'{m}_end'
                    if start_col in product and end_col in product:
                        if pd.notna(product[start_col]) and pd.notna(product[end_col]):
                            gantt_data.append({
                                "product": product_id,
                                "machine": m,
                                "start": float(product[start_col]),
                                "end": float(product[end_col]),
                                "duration": float(product[end_col] - product[start_col])
                            })

        # Prepare response
        response = {
            "status": "success",
            "config": {
                "sim_time": config.sim_time,
                "interarrival_mean": config.interarrival_mean,
                "warmup_time": config.warmup_time
            },
            "metrics": {
                "throughput_per_hour": float(round(metrics['throughput_per_hour'], 2)),
                "total_completed": int(metrics['total_completed']),
                "avg_lead_time": float(round(metrics['avg_lead_time'], 2)),
                "avg_utilization": float(round(metrics['avg_utilization'], 4)),
                "avg_wip": float(round(metrics.get('avg_wip', 0), 2)),
                "max_wip": int(metrics.get('max_wip', 0))
            },
            "charts": {
                "queue_over_time": queue_data,
                "wip_over_time": wip_data,
                "production_over_time": production_data,
                "lead_time_hist": lead_time_hist,
                "machine_status": machine_status,
                "gantt": gantt_data
            },
            "financial": {
                "labor_cost": float(financial_data['labor_cost']),
                "energy_cost": float(financial_data['energy_cost']),
                "downtime_cost": float(financial_data['downtime_cost']),
                "holding_cost": float(financial_data['holding_cost']),
                "total_cost": float(financial_data['total_cost'])
            },
            "bottleneck": {
                "machine": str(df_bottleneck.iloc[0]['machine']),
                "score": float(round(df_bottleneck.iloc[0]['bottleneck_score'], 3)),
                "utilization": float(round(df_bottleneck.iloc[0]['utilization'], 3))
            } if not df_bottleneck.empty else None,
            "machines": [
                {k: (int(v) if isinstance(v, (int, float)) and k in ['capacity', 'processed'] else float(v) if isinstance(v, (int, float)) else str(v))
                 for k, v in record.items()}
                for record in df_mstats.to_dict(orient='records')
            ]
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@app.post("/api/optimize")
def run_optimization(config: SimulationConfig):
    """
    Run optimization to find best machine configuration
    """
    try:
        from src.optimization import grid_search_optimization
        
        # Limit constraints for API safety
        # e.g. Max cost hardcoded or passed safely
        
        df_results, best_config = grid_search_optimization(
            target_throughput=None, # Optimize for max throughput/score
            max_cost=1000, # Default constraint
            sim_time=config.sim_time,
            num_replications=1, # Speed over precision for web demo
            verbose=False
        )
        
        # Convert df to records
        top_configs = df_results.nlargest(5, 'score').head(5).fillna(0).to_dict(orient='records')
        
        return {
            "status": "success",
            "best_config": {k: float(v) for k, v in best_config.items() if isinstance(v, (int, float, np.number))},
            "top_configs": [
                {k: (float(v) if isinstance(v, (int, float, np.number)) else str(v)) for k, v in r.items()}
                for r in top_configs
            ]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")


@app.post("/api/validate")
def validate_digital_twin(config: SimulationConfig):
    """
    Compare simulation against real-world data (Digital Twin Mode)
    """
    try:
        from src.analysis import compare_real_vs_sim
        import pandas as pd
        
        # Load real data
        real_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'real_production_log.csv')
        
        if not os.path.exists(real_data_path):
            # Generate if missing
            from src.generate_real_data import generate_real_data
            generate_real_data()
            
        df_real = pd.read_csv(real_data_path)
        
        # Run Simulation
        env = simpy.Environment()
        model = ProductionLineModel(
            env, 
            MACHINES, 
            config.interarrival_mean,
            warmup_time=config.warmup_time
        )
        env.run(until=config.sim_time)
        df_sim = model.collect_results()
        
        # Calculate Validation Metrics
        validation_metrics = compare_real_vs_sim(df_real, df_sim, config.sim_time)
        
        # Prepare comparison data for charts
        
        # 1. Throughput Comparison
        th_real = len(df_real) / (config.sim_time / 60.0)
        th_sim = len(df_sim) / (config.sim_time / 60.0)
        
        # 2. Lead Time Distribution
        # Histogram bins
        def get_hist_data(df, col='lead_time', bins=10):
            if df.empty or col not in df: return [], []
            hist, bin_edges = np.histogram(df[col], bins=bins)
            labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(hist))]
            return labels, [int(h) for h in hist]
            
        real_labels, real_hist = get_hist_data(df_real)
        sim_labels, sim_hist = get_hist_data(df_sim)
        
        return {
            "status": "success",
            "metrics": {k: float(v) for k, v in validation_metrics.items()},
            "comparison": {
                "throughput": {"real": th_real, "sim": th_sim},
                "lead_time_hist": {
                    "labels": real_labels, # Use real bins for both? ideally re-bin common range
                    "real": real_hist,
                    "sim": sim_hist
                }
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


# Vercel serverless handler
handler = app
