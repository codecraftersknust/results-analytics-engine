from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd
import sys
import os
import shutil
import uuid
from typing import List

# Ensure src is in pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.engine import metrics, insights, nlp, ingest

# Global State for Data
DATA_CACHE = {}
UPLOAD_DIR = "data/uploads"
NORMALIZED_FILE = "normalized_results.csv"

# Create upload dir if not exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load CSV data into memory on startup."""
    try:
        # Load default normalized file if exists
        csv_path = NORMALIZED_FILE
        if not os.path.exists(csv_path):
             csv_path = os.path.join("..", "..", NORMALIZED_FILE)
             
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            DATA_CACHE["df"] = df
            print(f"Loaded {len(df)} records from {csv_path}.")
        else:
            print(f"Default data {csv_path} not found. Waiting for upload.")
            DATA_CACHE["df"] = pd.DataFrame()
            
    except Exception as e:
        print(f"Error loading data: {e}")
        DATA_CACHE["df"] = pd.DataFrame()
        
    yield
    DATA_CACHE.clear()

app = FastAPI(
    title="Academic Analytics Engine API",
    description="API for accessing student academic performance insights",
    version="1.1.0",
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

# --- Ingestion Endpoints ---

@app.post("/api/v1/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a raw CSV file. Returns a dataset_id.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    dataset_id = str(uuid.uuid4())
    file_location = os.path.join(UPLOAD_DIR, f"{dataset_id}_{file.filename}")
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    return {
        "message": "File uploaded successfully",
        "dataset_id": dataset_id,
        "filename": file.filename,
        "status": "pending_processing"
    }

@app.post("/api/v1/datasets/{dataset_id}/process")
def process_dataset(dataset_id: str, background_tasks: BackgroundTasks):
    """
    Trigger processing (normalization + loading) of an uploaded dataset.
    """
    # Find the file
    files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(dataset_id)]
    if not files:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    raw_path = os.path.join(UPLOAD_DIR, files[0])
    
    try:
        # Load raw
        raw_df = pd.read_csv(raw_path)
        
        # Validate
        if not ingest.validate_schema(raw_df):
             raise HTTPException(status_code=400, detail="Invalid schema. Required columns missing.")
             
        # Normalize
        normalized_df = ingest.normalize_dataset(raw_df)
        
        # Save Normalized
        processed_path = os.path.join(UPLOAD_DIR, f"{dataset_id}_normalized.csv")
        normalized_df.to_csv(processed_path, index=False)
        
        # Load into Memory (Active Dataset)
        DATA_CACHE["df"] = normalized_df
        
        return {
            "message": "Dataset processed and loaded successfully",
            "records": len(normalized_df),
            "status": "active"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# --- Analytics Endpoints ---

# --- Endpoints ---

@app.get("/api/v1/students")
def list_students(limit: int = 100, search: str = ""):
    df = DATA_CACHE.get("df")
    if df is None or df.empty:
         raise HTTPException(status_code=503, detail="Data not loaded")
    
    # Get unique students
    # We assume 'student_id' exists. If 'name' existed we would return that too.
    unique_students = df[["student_id"]].drop_duplicates()
    
    if search:
        unique_students = unique_students[unique_students["student_id"].astype(str).str.contains(search)]
    
    # Pagination
    results = unique_students.head(limit).to_dict(orient="records")
    
    return {
        "count": len(unique_students),
        "results": results
    }

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

