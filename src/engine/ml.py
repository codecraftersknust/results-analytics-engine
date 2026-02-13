import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Optional

class SubjectAnalyzer:
    """
    Analyzes relationships between subjects using PCA (Principal Component Analysis) and difficulty modeling.
    
    This class identifies underlying patterns in how students perform across different subjects.
    It calculates:
    1. Subject Difficulty: Based on average scores (lower average = higher difficulty).
    2. Subject Relationships: Using PCA to map subjects into a 2D latent space where distance implies correlation.
    """
    def __init__(self, normalized_df: pd.DataFrame):
        self.df = normalized_df

    def analyze_subjects(self) -> Dict[str, Any]:
        """
        Returns subject analysis including difficulty and latent factor coordinates.
        
        The 'latent factors' (x, y coordinates) allow us to visualize which subjects are similar.
        Subjects close together in the 2D plot tend to have students who perform similarly in both.
        """
        # 1. Subject Difficulty (Inverse of Average Score)
        # We define difficulty as 100 - mean_score. A score of 90 implies 10 difficulty.
        subject_stats = self.df.groupby("subject")["score"].agg(["mean", "count"]).reset_index()
        subject_stats["difficulty"] = 100 - subject_stats["mean"]
        
        # 2. Latent Relationships (PCA)
        # Pivot: Rows=Students, Cols=Subjects, Values=Score
        # We create a matrix where each row represents a student and each column a subject.
        student_subject_matrix = self.df.groupby(["student_id", "subject"])["score"].mean().unstack()
        
        # Fill missing values with subject mean (Imputation)
        # If a student didn't take a subject, we assume they would perform 'averagely' in it
        # to avoid skewing the PCA with zeros or dropping valuable data.
        student_subject_matrix = student_subject_matrix.fillna(student_subject_matrix.mean())
        
        # If we still have NaNs (e.g. a subject no one took?), drop them
        student_subject_matrix = student_subject_matrix.dropna(axis=1, how='all')
        
        if student_subject_matrix.shape[1] < 2:
             return {"error": "Not enough subjects for relationship analysis"}
             
        # Standardize the data
        # PCA requires data to be centered and scaled (mean=0, variance=1) so that
        # subjects with larger score ranges don't dominate the variance.
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(student_subject_matrix.T) # Transpose so Rows=Subjects
        
        # PCA - Reduce to 2D for visualization
        # We project the high-dimensional subject data into just 2 dimensions (Latent Factors).
        pca = PCA(n_components=2)
        coords = pca.fit_transform(X_scaled)
        
        # Combine Results
        analysis_results = []
        subjects = student_subject_matrix.columns
        
        for i, subject in enumerate(subjects):
            stats = subject_stats[subject_stats["subject"] == subject].iloc[0]
            analysis_results.append({
                "subject": subject,
                "x": round(coords[i, 0], 2), # Latent Factor 1 (e.g., 'Analytical Ability')
                "y": round(coords[i, 1], 2), # Latent Factor 2 (e.g., 'Rote Memorization')
                "difficulty": round(stats["difficulty"], 1),
                "avg_score": round(stats["mean"], 1),
                "student_count": int(stats["count"])
            })
            
        return {
            "subjects": analysis_results,
            "variance_explained": [round(v, 2) for v in pca.explained_variance_ratio_]
        }


class PerformanceForecaster:
    """
    Predicts future student performance using Linear Regression on their historical data.
    """
    def __init__(self, normalized_df: pd.DataFrame):
        self.df = normalized_df

    def forecast_next_semester(self, student_id: str) -> Optional[Dict[str, Any]]:
        # Get student history
        student_history = self.df[self.df["student_id"] == student_id].copy()
        
        if student_history.empty:
            return None
            
        # Group by time_index to get average score per semester
        # We treat 'time_index' as our X axis (Time) and 'score' as our Y axis (Performance).
        semester_avgs = student_history.groupby("time_index")["score"].mean().reset_index()
        
        if len(semester_avgs) < 2:
             return {
                "student_id": student_id,
                "predicted_score": None, 
                "confidence": 0.0,
                "message": "Not enough history to forecast."
             }
             
        # Prepare Regression Data
        X = semester_avgs[["time_index"]].values
        y = semester_avgs["score"].values
        
        # Simple Linear Regression (y = mx + c)
        # Finds the line that best fits the student's trajectory.
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next time index
        next_time_index = semester_avgs["time_index"].max() + 1
        predicted_score = model.predict([[next_time_index]])[0]
        
        # Clip score to realistic bounds (0-100)
        predicted_score = max(0, min(100, predicted_score))
        
        # Calculate Confidence (R-squared)
        # R^2 indicates how well the line fits the data points.
        # High R^2 perans the student's performance is consistent and predictable.
        confidence = model.score(X, y)
        
        return {
            "entity": "student",
            "entity_id": student_id,
            "predicted_score": round(predicted_score, 1),
            "time_index": int(next_time_index),
            "confidence": round(max(0, confidence), 2)
        }

class RiskDetector:
    """
    Identifies students likely to fail or significantly decline based on heuristic signals.
    """
    def __init__(self, normalized_df: pd.DataFrame):
        self.df = normalized_df
        
    def assess_student_risk(self, student_id: str) -> Dict[str, Any]:
        student_history = self.df[self.df["student_id"] == student_id].copy()
        
        if student_history.empty:
            return {"risk_level": "unknown", "probability": 0.0, "signals": []}
            
        # Calculate Base Metrics
        scores = student_history["score"].values
        avg_score = scores.mean()
        std_dev = scores.std() if len(scores) > 1 else 0
        
        # Calculate Trend Slope (improvement/decline rate)
        try:
            time_idxs = student_history["time_index"].values
            slope = np.polyfit(time_idxs, scores, 1)[0] if len(scores) > 1 else 0
        except:
            slope = 0
            
        # Check for Recent Drop (Sudden decline in last recorded semester)
        recent_drop = False
        if len(scores) >= 2:
            recent_drop = (scores[-2] - scores[-1]) > 10
            
        # --- Risk Scoring Logic (Heuristic Probability Model) ---
        # We start at 0 risk and add probability based on negative signals.
        risk_score = 0.0
        signals = []
        
        # 1. Performance Risk (Base probability from low average)
        if avg_score < 50:
            risk_score += 0.4
            signals.append("RISK_LOW_AVG")
        elif avg_score < 60:
            risk_score += 0.2
            
        # 2. Trend Risk (Steep decline over time)
        if slope < -5:
            risk_score += 0.3
            signals.append("RISK_TREND_STEEP_DOWN")
        elif slope < -2:
            risk_score += 0.15
            signals.append("RISK_TREND_DOWN")
            
        # 3. Variance Risk (Inconsistent performance)
        if std_dev > 15:
            risk_score += 0.1
            signals.append("RISK_HIGH_VAR")
            
        # 4. Sudden Drop Risk (Immediate concern)
        if recent_drop:
            risk_score += 0.15
            signals.append("RISK_SUDDEN_DROP")
            
        # Cap probability at 0.95 (95%)
        probability = min(0.95, risk_score)
        
        # Determine Risk Level Label
        if probability > 0.7:
            level = "CRITICAL"
        elif probability > 0.4:
            level = "MODERATE"
        else:
            level = "LOW"
            
        latest_time = int(student_history["time_index"].max()) if "time_index" in student_history.columns else None

        return {
            "entity": "student",
            "entity_id": student_id,
            "label": level,
            "probability": round(probability, 2),
            "factors": signals,
            "time_index": latest_time
        }


class FeatureExtractor:
    """
    Transforms raw student data into a feature matrix suitable for Machine Learning clustering.
    
    Extracts 3 key features for each student:
    1. Overall Average Score: Measure of competence.
    2. Consistency (Std Dev): Measure of reliability (Lower is better).
    3. Improvement Rate (Slope): Measure of potential (Positive is better).
    """
    def __init__(self, normalized_df: pd.DataFrame):
        self.df = normalized_df

    def extract_features(self) -> pd.DataFrame:
        # 1. Overall Average
        avgs = self.df.groupby("student_id")["score"].mean()

        # 2. Consistency (Standard Deviation)
        # Fill NaN with 0 for students with only 1 record (std dev is undefined for n=1)
        consistency = self.df.groupby("student_id")["score"].std().fillna(0)

        # 3. Improvement Rate (Slope of score vs time)
        # We calculate the slope of the linear regression line for each student's history.
        def calc_slope(group):
            if len(group) < 2:
                return 0.0
            x = group["time_index"]
            y = group["score"]
            try:
                slope = np.polyfit(x, y, 1)[0]
                return slope
            except:
                return 0.0

        slopes = self.df.groupby("student_id").apply(calc_slope)

        # Assemble the Feature Matrix
        features = pd.DataFrame({
            "average_score": avgs,
            "consistency_std": consistency,
            "improvement_slope": slopes
        })
        
        # Fill NaNs if any remain (safety)
        features = features.fillna(0)
        
        return features

class StudentClusterModel:
    """
    Uses K-Means clustering to segment students into distinct profiles based on their performance features.
    
    Profiles identified (heuristically labeled):
    - Consistent High Performer
    - Volatile High Performer
    - Recovering / Improving
    - At Risk / Declining
    """
    def __init__(self, n_clusters=4):
        self.n_clusters = n_clusters
        # K-Means algorithm attempts to find 'n' centers in the data such that distance is minimized.
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.scaler = StandardScaler()
        self.labels = None
        self.cluster_centers = None
        self.feature_columns = ["average_score", "consistency_std", "improvement_slope"]

    def train(self, features_df: pd.DataFrame):
        """
        Trains the K-Means model on the provided features.
        """
        X = features_df[self.feature_columns]
        # Important: Scale features so that 'average_score' (0-100) doesn't dominate 'slope' (small decimals).
        X_scaled = self.scaler.fit_transform(X)
        self.kmeans.fit(X_scaled)
        
        self.labels = self.kmeans.labels_
        # Store centers in original scale for easier interpretation
        self.cluster_centers = self.scaler.inverse_transform(self.kmeans.cluster_centers_)
        
        return self.labels

    def get_student_cluster(self, student_id: str, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Predicts the cluster for a specific student and returns the labeled profile.
        """
        if student_id not in features_df.index:
            return None

        # Get student's feature vector
        student_features = features_df.loc[[student_id], self.feature_columns]
        student_scaled = self.scaler.transform(student_features)
        
        # Predict cluster ID
        cluster_id = self.kmeans.predict(student_scaled)[0]
        
        # Calculate Confidence Score
        # We use the inverse of the distance to the cluster center.
        # Closer to center = Higher confidence that they belong to this profile.
        distances = self.kmeans.transform(student_scaled)[0]
        min_dist = distances[cluster_id]
        confidence = 1.0 / (1.0 + min_dist)
        
        # Get Human-Readable Profile Name
        profile_name = self._describe_cluster(cluster_id)
        
        return {
            "entity": "student",
            "entity_id": student_id,
            "label": profile_name,
            "cluster_id": int(cluster_id),
            "confidence": round(confidence, 2),
            "features": student_features.to_dict(orient="records")[0]
        }

    def _describe_cluster(self, cluster_id: int) -> str:
        """
        Heuristic labeling of clusters based on their centroids.
        Because K-Means clusters are unlabelled, we look at the average values of the center
        to determine what "kind" of profile this is.
        """
        center = self.cluster_centers[cluster_id]
        avg_score = center[0]
        std_dev = center[1]
        slope = center[2]
        
        # Logic to assign names based on feature characteristics
        if avg_score > 75:
            if std_dev < 10:
                return "Consistent High Performer"
            else:
                return "Volatile High Performer"
        elif avg_score < 50:
            if slope > 0:
                return "Recovering / Improving"
            else:
                return "At Risk"
        else:
            # Mid range performance
            if slope > 2:
                return "Fast Improver"
            elif slope < -2:
                return "Declining Performance"
            elif std_dev > 15:
                return "Inconsistent Performer"
            else:
                return "Steady Average"
