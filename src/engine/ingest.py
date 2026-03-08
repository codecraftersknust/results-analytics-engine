import pandas as pd
import pdfplumber
import os
from typing import List, Dict, Any, Optional

# Expected columns for minimal validation (can be mapped)
REQUIRED_COLUMNS = ["University_Roll_No", "Semester"] 

# Config (could be passed in dynamically later)
SEMESTERS_PER_YEAR = 2 
SUBJECT_COLUMNS = [
    "Subject_1", "Subject_2", "Subject_3", "Subject_4", "Subject_5", "Subject_6",
    # Add common fallbacks for heuristics
    "Mathematics", "Physics", "Chemistry", "Biology", "English", "History"
]

ID_MAPPING = {
    "University_Roll_No": "student_id",
    "College_Name": "institution",
    "Batch": "batch",
    "Semester": "semester"
}

def parse_file(file_path: str) -> pd.DataFrame:
    """
    Universal ingestion entry point. Reads CSV, Excel, or PDF.
    Returns a unified raw Pandas DataFrame.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    elif ext == ".pdf":
        return extract_table_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def extract_table_from_pdf(file_path: str) -> pd.DataFrame:
    """
    Heuristic rule-based PDF table extractor using pdfplumber.
    It scans all pages, looks for the largest continuous table that has headers,
    and returns it as a DataFrame.
    """
    all_rows = []
    
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                # Clean up empty cells/newlines
                cleaned_table = []
                for row in table:
                    cleaned_row = [str(cell).replace('\\n', ' ').strip() if cell else None for cell in row]
                    cleaned_table.append(cleaned_row)
                    
                if len(cleaned_table) > 1:
                    # If this is the first page/table, assume first row is header
                    if not all_rows:
                        all_rows.extend(cleaned_table)
                    else:
                        # Skip header on subsequent pages if it matches the first table's header roughly
                        if cleaned_table[0] == all_rows[0]:
                            all_rows.extend(cleaned_table[1:])
                        else:
                            all_rows.extend(cleaned_table)
                            
    if not all_rows:
        raise ValueError("Could not extract any tabular data from the PDF.")
        
    df = pd.DataFrame(all_rows[1:], columns=all_rows[0])
    
    # Clean up column names (remove newlines, extra spaces)
    df.columns = [str(col).replace('\n', ' ').strip() for col in df.columns]
    
    # Try to cast numeric columns back to float where applicable
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
        
    return df

def validate_schema(df: pd.DataFrame) -> bool:
    """
    Checks if the dataframe has the minimum required columns to be processed.
    Uses fuzzy matching / heuristics.
    """
    df_cols = [str(c).lower().strip() for c in df.columns]
    
    # We look for ANY identifier that could be a student ID
    possible_id_cols = ["university_roll_no", "student_id", "id", "roll_no", "rollno", "student"]
    has_id = any(col in df_cols for col in possible_id_cols)
    
    # If the file doesn't have an ID column, we can't process it at all
    if not has_id:
        return False
        
    return True

def normalize_dataset(df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Converts a raw wide-format dataframe into the standard long-format normalized schema.
    Applies heuristic fallbacks for missing columns.
    """
    # 1. Standardize column names (strip whitespace)
    df.columns = [str(x).strip() for x in df.columns]
    
    # 2. Rename columns using mapping
    lower_mapping = {k.lower(): v for k, v in ID_MAPPING.items()}
    # Add heuristic fallbacks
    lower_mapping.update({
        "id": "student_id",
        "rollno": "student_id",
        "roll_no": "student_id",
        "student": "student_id"
    })
    
    new_cols = {}
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in lower_mapping:
            new_cols[col] = lower_mapping[col_lower]
        else:
            new_cols[col] = col
    df.rename(columns=new_cols, inplace=True)
    
    # If 'student_id' wasn't resolved, but we passed validation, force the first col as ID as a last resort
    if "student_id" not in df.columns:
        df = df.rename(columns={df.columns[0]: "student_id"})
    
    # 3. Basic cleaning
    df = df.drop(
        columns=[c for c in ["semester avg", "overall avg", "Total", "Results", "Div"] if c in df.columns],
        errors="ignore"
    )

    # 4. Handle Missing Optional Schema Columns
    if "institution" not in df.columns:
        df["institution"] = "Default University"
    if "batch" not in df.columns:
        df["batch"] = 1
        
    # Heuristics for Semester (if missing, assume Semester 1)
    if "semester" not in df.columns:
        df["semester"] = 1
        
    if df["semester"].dtype == object:
        df["semester_num"] = df["semester"].astype(str).str.extract(r'(\d+)').astype(float)
    else:
        df["semester_num"] = pd.to_numeric(df["semester"], errors="coerce")

    # Fill NaN semesters with 1
    df["semester_num"] = df["semester_num"].fillna(1)

    # 5. Derive Year & Term
    df["year"] = ((df["semester_num"] - 1) // SEMESTERS_PER_YEAR) + 1
    df["term"] = ((df["semester_num"] - 1) % SEMESTERS_PER_YEAR) + 1

    df["time_label"] = (
        "Year " + df["year"].astype(int).astype(str) +
        " Sem " + df["term"].astype(int).astype(str)
    )
    df["time_index"] = df["semester_num"].astype(int)

    # 6. Melt / Unpivot to Long Format
    normalized_rows = []
    
    # Fuzzy match available subjects
    available_subjects = []
    for col in df.columns:
        col_str = str(col).strip()
        if col_str in SUBJECT_COLUMNS or "Subject_" in col_str:
            available_subjects.append(col)
    
    if not available_subjects:
         raise ValueError("No subject columns found in dataset.")

    for _, row in df.iterrows():
        for subject_col in available_subjects:
            score = row.get(subject_col)

            # Clean score (in case of PDF string parsing)
            if isinstance(score, str):
                score = ''.join(filter(str.isdigit, score))
            
            try:
                score = float(score)
            except (ValueError, TypeError):
                continue
                
            if pd.isna(score):
                continue

            normalized_rows.append({
                "student_id": row.get("student_id"),
                "institution": row.get("institution", "Unknown"),
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
