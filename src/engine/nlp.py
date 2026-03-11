from typing import Dict, Any
from .insights import Insight
from . import llm_client
import json

TEMPLATES = {
    "improvement": "Student {student_id} improved their average score by {delta:.1f} points in {time_label} (from {prev_score:.1f} to {avg_score:.1f}).",
    "decline": "Student {student_id} saw a decline of {delta:.1f} points in {time_label} (from {prev_score:.1f} to {avg_score:.1f}).",
    "correlation": "There is a strong connection between {subject_a} and {subject_b} (correlation: {correlation:.2f}). Students performing well in one tend to do well in the other."
}

def generate_base_string(insight: Insight) -> str:
    """Generates the static fallback string."""
    template = TEMPLATES.get(insight.type)
    if not template:
        return f"Insight: {insight.description_template} (Data: {insight.data})"
    
    context = insight.data.copy()
    if insight.scope == "student":
        context["student_id"] = insight.entity_id
        
    try:
        return template.format(**context)
    except KeyError as e:
        return f"Error formatting insight: missing key {e}"

def explain_insight(insight: Insight) -> str:
    """
    Converts a structured Insight object into a human-readable string.
    Uses Google Gemini 2.5 Flash for dynamic generation, with a static fallback.
    """
    base_string = generate_base_string(insight)
    
    # Check if Gemini API is available
    if not llm_client.GEMINI_API_KEY:
        return base_string
        
    try:
        model = llm_client.get_gemini_model("gemini-2.5-flash")
        
        prompt = (
            f"You are an academic advisor AI analyzing student performance for a teacher's dashboard. "
            f"Rewrite the following basic data insight into a natural, encouraging, and highly readable sentence. "
            f"CRITICAL: You must refer to the student in the THIRD PERSON (e.g., 'The student', or their ID), not 'you'.\n\n"
            f"Raw Data: {json.dumps(insight.data)}\n"
            f"Basic Insight: {base_string}\n\n"
            f"Rule: Return ONLY the rewritten sentence, nothing else."
        )
        
        # We ensure it's not strictly JSON, just standard text output for NLP
        response = model.generate_content(prompt)
        ai_insight = response.text.strip()
        
        if ai_insight:
            return ai_insight
            
    except Exception as e:
        print(f"NLP Generation failed (falling back to static templates): {e}")

    # Fallback to standard template if AI generation fails
    return base_string
