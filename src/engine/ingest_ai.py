import json
import base64
from typing import Optional, Dict, Any
import pandas as pd
from pydantic import BaseModel, Field

from src.engine import llm_client

# Define the precise schema we want the AI to return.
# Using Pydantic helps us define the structure clearly for Gemini's structured output.
class StudentRecord(BaseModel):
    student_id: str = Field(description="The unique identifier or roll number for the student.")
    institution: str = Field(description="The name of the college or university.")
    batch: str = Field(description="The batch or enrollment year.")
    semester_num: int = Field(description="The numerical semester (e.g., 1, 2, 3).")
    year: int = Field(description="The academic year (e.g., 1, 2).")
    term: int = Field(description="The term within the year, usually 1 or 2.")
    time_label: str = Field(description="Human readable string, e.g., 'Year 1 Sem 1'.")
    time_index: int = Field(description="Numerical global order of time, matching semester_num.")
    subject: str = Field(description="The exact name of the subject or course.")
    score: float = Field(description="The numeric score the student received.")

class DatasetOutput(BaseModel):
    records: list[StudentRecord] = Field(description="List of all extracted student results.")

class LLMDataExtractor:
    """
    Uses Google Gemini 1.5 Pro to extract tabular academic data from unstructured files
    (like messy PDFs or arbitrary Excel layouts) into a strict normalized Pandas DataFrame.
    """
    def __init__(self):
        self.model = llm_client.get_gemini_model("gemini-2.5-flash")

    def extract_from_file(self, file_path: str, mime_type: str) -> pd.DataFrame:
        """
        Uploads the file to the Gemini API and extracts data.
        Returns a normalized Pandas DataFrame.
        """
        print(f"Uploading {file_path} to Gemini API...")
        
        # 1. Provide instructions
        prompt = (
            "You are an expert data extraction system. I am providing you with an academic unstructured dataset file "
            "(it could be a raw CSV, a messy Excel file, or a scanned PDF).\n\n"
            "Your task:\n"
            "1. Read through the entire file's content.\n"
            "2. Extract every single academic grade/score for every student across every subject.\n"
            "3. If fields like 'institution' or 'batch' are missing, use 'Unknown'.\n"
            "4. If 'semester' is missing, assume it is 1.\n"
            "5. Convert the 'semester' to a numerical 'semester_num', 'year' (assume 2 semesters per year), "
            "and 'term'. Set 'time_index' equal to 'semester_num', and 'time_label' to 'Year X Sem Y'.\n"
            "6. You MUST return the data exactly matching the requested JSON schema array."
        )

        try:
            # For Gemini, we can pass small text files directly, but for PDFs we need to upload
            # them via the File API for processing. We'll use the generic parts list approach.
            
            with open(file_path, "rb") as f:
                doc_data = f.read()
                
            file_part = {
                "mime_type": mime_type,
                "data": doc_data
            }

            # 2. Call the API enforcing structured JSON output
            print("Processing with Gemini 1.5 Pro (This may take 10-20 seconds)...")
            response = self.model.generate_content(
                contents=[prompt, file_part],
                generation_config=llm_client.genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=DatasetOutput,
                    temperature=0.0, # Zero temp for strict data extraction
                )
            )

            # 3. Parse JSON response
            result_json = json.loads(response.text)
            records = result_json.get("records", [])
            
            if not records:
                 raise ValueError("Gemini returned zero records. File may be empty or unreadable.")
                 
            # 4. Convert to DataFrame
            df = pd.DataFrame(records)
            return df

        except Exception as e:
            raise RuntimeError(f"LLM Extraction failed: {str(e)}")
