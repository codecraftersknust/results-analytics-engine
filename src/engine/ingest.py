import pandas as pd
from typing import List, Dict, Any, Optional

# Expected columns for minimal validation (can be mapped)
REQUIRED_COLUMNS = ["University_Roll_No", "Semester"] 

# Config (could be passed in dynamically later)
SEMESTERS_PER_YEAR = 2 
SUBJECT_COLUMNS = [
    "Subject_1", "Subject_2", "Subject_3", "Subject_4", "Subject_5", "Subject_6"
]
ID_MAPPING = {
    "University_Roll_No": "student_id",
    "College_Name": "institution",
    "Batch": "batch",
    "Semester": "semester"
}

def validate_schema(df: pd.DataFrame) -> bool:
    """
    Checks if the dataframe has the minimum required columns to be processed.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        # Check if they are already normalized?
        if "student_id" in df.columns and "score" in df.columns:
             return True # Already normalized
        return False
    return True

def normalize_dataset(df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Converts a raw wide-format dataframe into the standard long-format normalized schema.
    """
    # 1. Rename columns
    df = df.rename(columns=ID_MAPPING)
    
    # 2. Basic cleaning
    # Drop derived columns if they exist in raw data to avoid conflicts
    df = df.drop(
        columns=[c for c in ["semester avg", "overall avg"] if c in df.columns],
        errors="ignore"
    )

    # 3. Ensure semester is numeric
    # If semester is strictly numeric string, convert. If "Sem 1", extract number.
    if df["semester"].dtype == object:
        df["semester_num"] = df["semester"].astype(str).str.extract(r'(\d+)').astype(float)
    else:
        df["semester_num"] = pd.to_numeric(df["semester"], errors="coerce")

    if df["semester_num"].isna().any():
        raise ValueError("Non-numeric semester values detected. Please check input data.")

    # 4. Derive Year & Term
    df["year"] = ((df["semester_num"] - 1) // SEMESTERS_PER_YEAR) + 1
    df["term"] = ((df["semester_num"] - 1) % SEMESTERS_PER_YEAR) + 1

    # Human-readable labels
    df["time_label"] = (
        "Year " + df["year"].astype(int).astype(str) +
        " Sem " + df["term"].astype(int).astype(str)
    )
    
    # Global ordering index
    df["time_index"] = df["semester_num"].astype(int)

    # 5. Melt / Unpivot to Long Format
    # We want one row per student per subject per semester
    normalized_rows = []
    
    # Identify which columns are subjects (intersection of known subjects and df columns)
    available_subjects = [col for col in SUBJECT_COLUMNS if col in df.columns]
    
    if not available_subjects:
         raise ValueError("No subject columns found in dataset.")

    for _, row in df.iterrows():
        for subject_col in available_subjects:
            score = row.get(subject_col)

            if pd.isna(score):
                continue

            normalized_rows.append({
                "student_id": row.get("student_id"),
                "institution": row.get("institution", "Unknown"), # Default if missing
                "batch": row.get("batch", "Unknown"),
                "semester": row["semester_num"],
                "year": row["year"],
                "term": row["term"],
                "time_label": row["time_label"],
                "time_index": row["time_index"],
                "subject": subject_col,
                "score": score
            })

    normalized_df = pd.DataFrame(normalized_rows)
    return normalized_df
