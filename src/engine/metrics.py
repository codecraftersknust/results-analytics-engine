import pandas as pd
import numpy as np

def calculate_student_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the average score for each student per semester/time_index.
    """
    # Group by student and time to get their average performance in that period
    avgs = df.groupby(["student_id", "time_index", "time_label"])["score"].mean().reset_index()
    avgs = avgs.rename(columns={"score": "average_score"})
    return avgs

def calculate_cohort_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the average score for each subject per semester (Global/Cohort view).
    """
    trends = df.groupby(["subject", "time_index", "time_label"])["score"].mean().reset_index()
    trends = trends.rename(columns={"score": "cohort_average_score"})
    return trends

def calculate_performance_deltas(student_avgs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the change in average score from the previous semester for each student.
    Expects student_avgs_df to be sorted by student_id and time_index.
    """
    df_sorted = student_avgs_df.sort_values(by=["student_id", "time_index"])
    
    # Calculate difference
    df_sorted["prev_score"] = df_sorted.groupby("student_id")["average_score"].shift(1)
    df_sorted["delta"] = df_sorted["average_score"] - df_sorted["prev_score"]
    df_sorted["delta_percent"] = (df_sorted["delta"] / df_sorted["prev_score"]) * 100
    
    return df_sorted

def calculate_subject_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the Pearson correlation correlation between subjects.
    Returns a pivot table or correlation matrix.
    """
    # Pivot to make subjects columns and students rows (one row per student, aggregation may be needed if multiple scores)
    # If we want general correlation, we treat every (student, time) pair as an observation, or just averages per student.
    # Let's pivot on student_id to see general affinity (Student A is good at X and Y across all time).
    # Taking mean score per student per subject first.
    
    student_subject_means = df.groupby(["student_id", "subject"])["score"].mean().unstack()
    
    # Calculate correlation matrix
    corr_matrix = student_subject_means.corr(method='pearson')
    
    return corr_matrix
