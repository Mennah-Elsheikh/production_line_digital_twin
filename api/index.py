"""
Mini FastAPI Backend for Vercel - Demo Version
This is a simplified standalone version for Vercel deployment.
For full functionality, use the local servers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import random

app = FastAPI(title="Production Line Digital Twin API - Demo")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationConfig(BaseModel):
    sim_time: int = 480
    interarrival_mean: float = 3.5
    warmup_time: float = 60

@app.get("/")
def root():
    return {
        "message": "Production Line Digital Twin API - Demo Mode",
        "note": "This is a simplified demo. For full features, use local servers.",
        "endpoints": ["/api/health", "/api/simulate", "/api/optimize", "/api/validate"]
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "digital-twin-api-demo", "mode": "vercel"}

@app.post("/api/simulate")
def run_simulation(config: SimulationConfig):
    """
    Demo simulation endpoint - returns mock data
    For real simulation, use local servers at localhost:8000
    """
    try:
        # Generate mock data for demo
        random.seed(42)
        num_products = int(config.sim_time / config.interarrival_mean)
        
        throughput = num_products / (config.sim_time / 60.0)
        
        response = {
            "status": "success",
            "mode": "demo",
            "note": "This is mock data for Vercel demo. Use local servers for real simulation.",
            "config": {
                "sim_time": config.sim_time,
                "interarrival_mean": config.interarrival_mean,
                "warmup_time": config.warmup_time
            },
            "metrics": {
                "throughput_per_hour": round(throughput, 2),
                "total_completed": num_products,
                "avg_lead_time": round(random.uniform(100, 150), 2),
                "avg_utilization": round(random.uniform(0.6, 0.8), 4),
                "avg_wip": round(random.uniform(20, 35), 2),
                "max_wip": random.randint(35, 50)
            },
            "charts": {
                "queue_over_time": [],
                "wip_over_time": [],
                "production_over_time": [
                    {"time": i * 10, "value": int(i * throughput / 6)} 
                    for i in range(0, int(config.sim_time / 10))
                ],
                "lead_time_hist": {
                    "labels": ["100-110", "110-120", "120-130", "130-140", "140-150"],
                    "data": [15, 25, 30, 20, 10]
                },
                "machine_status": [
                    {"machine": "Cutting", "busy": 75.5, "idle": 24.5},
                    {"machine": "Drilling", "busy": 68.2, "idle": 31.8},
                    {"machine": "Assembly", "busy": 62.3, "idle": 37.7},
                    {"machine": "Painting", "busy": 58.1, "idle": 41.9}
                ],
                "gantt": []
            },
            "financial": {
                "labor_cost": 2400.0,
                "energy_cost": 360.0,
                "downtime_cost": 180.0,
                "holding_cost": 140.0,
                "total_cost": 3080.0
            },
            "bottleneck": {
                "machine": "Cutting",
                "score": 0.856,
                "utilization": 0.755
            },
            "machines": [
                {"machine": "Cutting", "capacity": 1, "processed": num_products, "utilization": 0.755},
                {"machine": "Drilling", "capacity": 1, "processed": num_products, "utilization": 0.682},
                {"machine": "Assembly", "capacity": 1, "processed": num_products, "utilization": 0.623},
                {"machine": "Painting", "capacity": 1, "processed": num_products, "utilization": 0.581}
            ]
        }
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "detail": f"Demo simulation error: {str(e)}"}
        )

@app.post("/api/optimize")
def run_optimization(config: SimulationConfig):
    """Demo optimization endpoint"""
    return {
        "status": "success",
        "mode": "demo",
        "note": "Mock optimization data. Use local servers for real optimization.",
        "best_config": {
            "cutting_capacity": 2,
            "drilling_capacity": 2,
            "assembly_capacity": 1,
            "painting_capacity": 1,
            "throughput_mean": 12.5,
            "implementation_cost": 400
        },
        "top_configs": [
            {"throughput_mean": 12.5, "implementation_cost": 400, "score": 0.875},
            {"throughput_mean": 11.8, "implementation_cost": 200, "score": 0.842},
            {"throughput_mean": 11.2, "implementation_cost": 0, "score": 0.801}
        ]
    }

@app.post("/api/validate")
def validate_digital_twin(config: SimulationConfig):
    """Demo validation endpoint"""
    return {
        "status": "success",
        "mode": "demo",
        "note": "Mock validation data. Use local servers for real validation.",
        "metrics": {
            "validation_score": 87.5,
            "throughput_error_%": 5.2,
            "lead_time_error_%": 3.8,
            "throughput_real": 11.2,
            "throughput_sim": 10.6,
            "lead_time_real": 118.5,
            "lead_time_sim": 114.0
        },
        "comparison": {
            "throughput": {"real": 11.2, "sim": 10.6},
            "lead_time_hist": {
                "labels": ["100-110", "110-120", "120-130", "130-140"],
                "real": [12, 28, 25, 15],
                "sim": [15, 25, 22, 18]
            }
        }
    }

# Vercel serverless handler
handler = app
