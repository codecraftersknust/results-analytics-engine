from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import pandas as pd

@dataclass
class Insight:
    type: str  # "improvement", "decline", "consistency", "correlation"
    scope: str # "student" or "cohort"
    entity_id: str # student_id or "global"
    description_template: str # Unformatted string for NLP layer
    data: Dict[str, Any] # Supporting data (numbers)
    confidence: float = 1.0

def generate_student_insights(deltas_df: pd.DataFrame) -> List[Insight]:
    """
    Generates insights based on student performance deltas.
    """
    insights = []
    
    # Thresholds
    IMPROVEMENT_THRESHOLD = 5.0
    DECLINE_THRESHOLD = -5.0
    
    for _, row in deltas_df.iterrows():
        if pd.isna(row["delta"]):
            continue
            
        student_id = str(row["student_id"])
        time_label = row["time_label"]
        delta = row["delta"]
        
        if delta >= IMPROVEMENT_THRESHOLD:
            insights.append(Insight(
                type="improvement",
                scope="student",
                entity_id=student_id,
                description_template="improved overall performance",
                data={
                    "delta": delta,
                    "avg_score": row["average_score"],
                    "prev_score": row["prev_score"],
                    "time_label": time_label
                }
            ))
        elif delta <= DECLINE_THRESHOLD:
            insights.append(Insight(
                type="decline",
                scope="student",
                entity_id=student_id,
                description_template="declined in overall performance",
                data={
                    "delta": delta,
                    "avg_score": row["average_score"],
                    "prev_score": row["prev_score"],
                    "time_label": time_label
                }
            ))
            
    return insights

def generate_cohort_correlations(corr_matrix: pd.DataFrame) -> List[Insight]:
    """
    Identifies strong correlations between subjects.
    """
    insights = []
    CORRELATION_THRESHOLD = 0.6
    
    # Iterate over correlation matrix
    # Since it's symmetric, we mask duplicates or just iterate carefully
    subjects = corr_matrix.columns
    seen_pairs = set()
    
    for subj_a in subjects:
        for subj_b in subjects:
            if subj_a == subj_b:
                continue
                
            pair = tuple(sorted([subj_a, subj_b]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            
            val = corr_matrix.loc[subj_a, subj_b]
            
            if val >= CORRELATION_THRESHOLD:
                insights.append(Insight(
                    type="correlation",
                    scope="cohort",
                    entity_id="global",
                    description_template="strong positive correlation",
                    data={
                        "subject_a": subj_a,
                        "subject_b": subj_b,
                        "correlation": val
                    }
                ))
    
    return insights
