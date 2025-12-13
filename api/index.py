"""
Minimal FastAPI for Vercel with complete response structure
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Production Line Digital Twin API - Demo"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "mode": "demo"}

@app.post("/api/simulate")
def simulate(data: dict = None):
    return {
        "status": "success",
        "mode": "demo",
        "config": {"sim_time": 480, "interarrival_mean": 3.5, "warmup_time": 60},
        "metrics": {
            "throughput_per_hour": 12.5,
            "total_completed": 100,
            "avg_lead_time": 120.0,
            "avg_utilization": 0.7,
            "avg_wip": 25.0,
            "max_wip": 45
        },
        "charts": {
            "queue_over_time": [{"time": i*10, "value": i} for i in range(48)],
            "wip_over_time": [{"time": i*10, "value": 20 + i} for i in range(48)],
            "production_over_time": [{"time": i*10, "value": i*2} for i in range(48)],
            "lead_time_hist": {
                "labels": ["100-110", "110-120", "120-130", "130-140", "140-150"],
                "data": [15, 25, 30, 20, 10]
            },
            "machine_status": [
                {"machine": "Cutting", "busy": 75.0, "idle": 25.0},
                {"machine": "Drilling", "busy": 68.0, "idle": 32.0},
                {"machine": "Assembly", "busy": 62.0, "idle": 38.0},
                {"machine": "Painting", "busy": 58.0, "idle": 42.0}
            ],
            "gantt": []
        },
        "bottleneck": {"machine": "Cutting", "score": 0.856, "utilization": 0.75},
        "machines": [
            {"machine": "Cutting", "capacity": 1, "processed": 100, "utilization": 0.75},
            {"machine": "Drilling", "capacity": 1, "processed": 100, "utilization": 0.68},
            {"machine": "Assembly", "capacity": 1, "processed": 100, "utilization": 0.62},
            {"machine": "Painting", "capacity": 1, "processed": 100, "utilization": 0.58}
        ],
        "financial": {
            "labor_cost": 2400.0,
            "energy_cost": 360.0,
            "downtime_cost": 180.0,
            "holding_cost": 140.0,
            "total_cost": 3080.0
        }
    }

@app.post("/api/optimize")
def optimize(data: dict = None):
    return {
        "status": "success",
        "mode": "demo",
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
def validate(data: dict = None):
    return {
        "status": "success",
        "mode": "demo",
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
