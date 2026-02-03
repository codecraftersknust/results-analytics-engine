import pandas as pd

# ---------- CONFIG ----------
INPUT_CSV = "results.csv"
OUTPUT_CSV = "n_results.csv"

SEMESTERS_PER_YEAR = 2  # <-- change here if needed

SUBJECT_COLUMNS = [
    "Subject_1",
    "Subject_2",
    "Subject_3",
    "Subject_4",
    "Subject_5",
    "Subject_6"
]

ID_COLUMNS = {
    "student_id": "student_id",
    "College_Name": "institution",
    "Batch": "batch",
    "Semester": "semester"
}
# ----------------------------


def normalize_dataset():
    # Load dataset
    df = pd.read_csv(INPUT_CSV)

    # Rename identifier columns
    df = df.rename(columns=ID_COLUMNS)

    # Drop derived columns if they exist
    df = df.drop(
        columns=[c for c in ["semester avg", "overall avg"] if c in df.columns],
        errors="ignore"
    )

    # Ensure semester is numeric
    df["semester_num"] = pd.to_numeric(df["semester"], errors="coerce")

    if df["semester_num"].isna().any():
        raise ValueError("Non-numeric semester values detected. Fix input data first.")

    # ---- DERIVE YEAR & TERM ----
    df["year"] = ((df["semester_num"] - 1) // SEMESTERS_PER_YEAR) + 1
    df["term"] = ((df["semester_num"] - 1) % SEMESTERS_PER_YEAR) + 1

    # Human-readable label
    df["time_label"] = (
        "Year " + df["year"].astype(int).astype(str) +
        " Sem " + df["term"].astype(int).astype(str)
    )

    # Global ordering index
    df["time_index"] = df["semester_num"].astype(int)

    normalized_rows = []

    # Normalize subject scores
    for _, row in df.iterrows():
        for subject_col in SUBJECT_COLUMNS:
            score = row.get(subject_col)

            if pd.isna(score):
                continue

            normalized_rows.append({
                "student_id": row["student_id"],
                "institution": row["institution"],
                "batch": row["batch"],
                "semester": row["semester_num"],
                "year": row["year"],
                "term": row["term"],
                "time_label": row["time_label"],
                "time_index": row["time_index"],
                "subject": subject_col,
                "score": score
            })

    normalized_df = pd.DataFrame(normalized_rows)

    # Save output
    normalized_df.to_csv(OUTPUT_CSV, index=False)

    print("Normalization + time derivation complete.")
    print(f"Original rows: {len(df)}")
    print(f"Normalized rows: {len(normalized_df)}")

if __name__ == "__main__":
    normalize_dataset()
