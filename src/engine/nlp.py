from .insights import Insight

TEMPLATES = {
    "improvement": "Student {student_id} improved their average score by {delta:.1f} points in {time_label} (from {prev_score:.1f} to {avg_score:.1f}).",
    "decline": "Student {student_id} saw a decline of {delta:.1f} points in {time_label} (from {prev_score:.1f} to {avg_score:.1f}).",
    "correlation": "There is a strong connection between {subject_a} and {subject_b} (correlation: {correlation:.2f}). Students performing well in one tend to do well in the other."
}

def explain_insight(insight: Insight) -> str:
    """
    Converts a structured Insight object into a human-readable string.
    """
    
    # 1. Select template based on type
    template = TEMPLATES.get(insight.type)
    
    if not template:
        return f"Insight: {insight.description_template} (Data: {insight.data})"
    
    # 2. Flatten data for formatting
    # We combine insight.data dict with specific keys like 'student_id' if needed
    context = insight.data.copy()
    if insight.scope == "student":
        context["student_id"] = insight.entity_id
        
    # 3. Format string
    try:
        return template.format(**context)
    except KeyError as e:
        return f"Error formatting insight: missing key {e}"
