import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from engine.metrics import calculate_student_averages, calculate_performance_deltas, calculate_subject_correlations
from engine.insights import generate_student_insights, generate_cohort_correlations
from engine.nlp import explain_insight

def main():
    print("Loading data...")
    try:
        df = pd.read_csv("normalized_results.csv")
    except FileNotFoundError:
        print("Error: normalized_results.csv not found.")
        return

    print(f"Loaded {len(df)} rows.")

    # 1. Metrics
    print("\n--- Computing Metrics ---")
    st_avgs = calculate_student_averages(df)
    deltas = calculate_performance_deltas(st_avgs)
    
    # Check for NaN in deltas (first semester has no delta)
    deltas_clean = deltas.dropna(subset=["delta"])
    
    print(f"Calculated deltas for {len(deltas_clean)} student-semester transitions.")
    
    corr_matrix = calculate_subject_correlations(df)
    print("Calculated correlation matrix.")

    # 2. Insights
    print("\n--- Generating Insights ---")
    student_insights = generate_student_insights(deltas_clean)
    cohort_insights = generate_cohort_correlations(corr_matrix)
    
    print(f"Found {len(student_insights)} student insights (Improvement/Decline).")
    print(f"Found {len(cohort_insights)} cohort insights (Correlations).")

    # 3. NLP / Output
    print("\n--- Sample Output (NLP) ---")
    
    print("[Student Insights]")
    for insight in student_insights[:5]:
        print(f" - {explain_insight(insight)}")
        
    print("\n[Cohort Insights]")
    for insight in cohort_insights:
        print(f" - {explain_insight(insight)}")

if __name__ == "__main__":
    main()
