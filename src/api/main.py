from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd
import sys
import os

# Ensure src is in pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.engine import metrics, insights, nlp

# Global State for Data
DATA_CACHE = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load CSV data into memory on startup."""
    try:
        # We need to look for the file relative to where the command is run, 
        # or use absolute path. Assuming run from root.
        csv_path = "normalized_results.csv"
        if not os.path.exists(csv_path):
             # Try looking one level up if run from src/api
             csv_path = "../../normalized_results.csv"
             
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            DATA_CACHE["df"] = df
            print(f"Loaded {len(df)} records from {csv_path}.")
        else:
            print(f"Error: {csv_path} not found!")
            DATA_CACHE["df"] = pd.DataFrame()
            
    except Exception as e:
        print(f"Error loading data: {e}")
        DATA_CACHE["df"] = pd.DataFrame()
        
    yield
    # Cleanup if needed
    DATA_CACHE.clear()

app = FastAPI(
    title="Academic Analytics Engine API",
    description="API for accessing student academic performance insights",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (Allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "records_loaded": len(DATA_CACHE.get("df", []))}

# --- Endpoints ---

@app.get("/api/v1/students/{student_id}/summary")
def get_student_summary(student_id: int):
    df = DATA_CACHE.get("df")
    if df is None or df.empty:
         raise HTTPException(status_code=503, detail="Data not loaded")

    # Filter for student
    student_df = df[df["student_id"] == student_id]
    
    if student_df.empty:
        raise HTTPException(status_code=404, detail="Student not found")

    # 1. Basic Stats
    total_avg = student_df["score"].mean()
    
    # 2. Insights
    # We need the full history averages to compute deltas
    all_avgs = metrics.calculate_student_averages(df)
    student_avgs = all_avgs[all_avgs["student_id"] == student_id]
    
    deltas = metrics.calculate_performance_deltas(student_avgs)
    raw_insights = insights.generate_student_insights(deltas)
    
    # NLP
    narrative_insights = [nlp.explain_insight(i) for i in raw_insights]
    
    return {
        "student_id": student_id,
        "overall_average": round(total_avg, 2),
        "total_semesters": student_df["semester"].nunique(),
        "insights": narrative_insights,
        "history": student_avgs.to_dict(orient="records")
    }

@app.get("/api/v1/cohort/trends")
def get_cohort_trends():
    df = DATA_CACHE.get("df")
    if df is None or df.empty:
         raise HTTPException(status_code=503, detail="Data not loaded")
         
    trends = metrics.calculate_cohort_trends(df)
    
    return {
        "trends": trends.to_dict(orient="records")
    }

@app.get("/api/v1/cohort/correlations")
def get_cohort_correlations():
    df = DATA_CACHE.get("df")
    if df is None or df.empty:
         raise HTTPException(status_code=503, detail="Data not loaded")
    
    # 1. Calculate Matrix
    corr_matrix = metrics.calculate_subject_correlations(df)
    
    # 2. Extract Key Insights (Strong correlations)
    insights_list = insights.generate_cohort_correlations(corr_matrix)
    narrative_insights = [nlp.explain_insight(i) for i in insights_list]
    
    # 3. Format full matrix for a Heatmap implementation on frontend
    # We return it as a list of {subject_a, subject_b, correlation}
    matrix_data = []
    for subj_a in corr_matrix.columns:
        for subj_b in corr_matrix.columns:
            matrix_data.append({
                "x": subj_a,
                "y": subj_b,
                "value": round(corr_matrix.loc[subj_a, subj_b], 3)
            })
            
    return {
        "insights": narrative_insights,
        "heatmap_data": matrix_data
    }

