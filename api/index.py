"""
Minimal FastAPI for Vercel - No complex imports
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
    return {"status": "ok", "message": "Production Line Digital Twin API"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.post("/api/simulate")
def simulate(data: dict = None):
    return {
        "status": "success",
        "mode": "demo",
        "metrics": {
            "throughput_per_hour": 12.5,
            "total_completed": 100,
            "avg_lead_time": 120.0,
            "avg_utilization": 0.7,
            "avg_wip": 25.0,
            "max_wip": 45
        },
        "charts": {
            "production_over_time": [{"time": i*10, "value": i*2} for i in range(48)],
            "machine_status": [
                {"machine": "Cutting", "busy": 75, "idle": 25},
                {"machine": "Drilling", "busy": 68, "idle": 32}
            ]
        },
        "bottleneck": {"machine": "Cutting", "score": 0.85, "utilization": 0.75},
        "machines": [
            {"machine": "Cutting", "capacity": 1, "processed": 100, "utilization": 0.75}
        ],
        "financial": {"total_cost": 3000.0}
    }

@app.post("/api/optimize")
def optimize(data: dict = None):
    return {
        "status": "success",
        "best_config": {"throughput_mean": 12.5},
        "top_configs": [{"throughput_mean": 12.5, "score": 0.85}]
    }

@app.post("/api/validate")
def validate(data: dict = None):
    return {
        "status": "success",
        "metrics": {"validation_score": 85.0},
        "comparison": {"throughput": {"real": 11, "sim": 10}}
    }
