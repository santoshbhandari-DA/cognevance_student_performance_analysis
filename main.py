"""
Student Performance Analysis
Cognevance Technologies - Level 1 (Easy)

What this script does:
  1. Loads the raw student, performance and attendance data
  2. Cleans the data (attendance text, homework %, invalid exam scores)
  3. Calculates attendance % for every student and subject
  4. Merges everything into one clean dataset
  5. Analyses marks, attendance and homework, and checks relationships
  6. Saves charts, the cleaned dataset and a text summary

Run:  python main.py
Needs: pandas, numpy, matplotlib
"""

import os

import matplotlib
matplotlib.use("Agg")  # lets the script save charts without opening windows
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------
# Read CSV files from the "data" folder if it exists, else the current folder
DATA_DIR = "data" if os.path.isdir("data") else "."
CHART_DIR = "charts"
OUTPUT_DIR = "output"
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

summary_lines = []  # everything we print is also saved to output/summary.txt


def show(text=""):
    """Print a line and also keep it for the summary file."""
    print(text)
    summary_lines.append(str(text))


# ----------------------------------------------------------------------
# Step 1: Load the data
# ----------------------------------------------------------------------
print("[1/6] Loading data...")
students = pd.read_csv(os.path.join(DATA_DIR, "students.csv"))
performance = pd.read_csv(os.path.join(DATA_DIR, "performance.csv"), dtype=str)
attendance = pd.read_csv(os.path.join(DATA_DIR, "attendance.csv"))

show(f"Students rows:    {len(students):,}")
show(f"Performance rows: {len(performance):,}")
show(f"Attendance rows:  {len(attendance):,}")

# ----------------------------------------------------------------------
# Step 2: Clean the attendance data
# ----------------------------------------------------------------------
# The status column has messy text: 'PRESENT ', ' late', 'absnt', ...
# We remove spaces, make everything lower case and fix the typo.
print("[2/6] Cleaning attendance data...")
attendance["status"] = (
    attendance["Attendance_Status"].astype(str).str.strip().str.lower()
)
attendance["status"] = attendance["status"].replace({"absnt": "absent"})

# Score for each status (these weights are an assumption of this project):
#   present = 1, late / excused = 0.5, absent / left early = 0
status_score = {
    "present": 1.0,
    "late": 0.5,
    "excused": 0.5,
    "absent": 0.0,
    "left early": 0.0,
}
attendance["att_score"] = attendance["status"].map(status_score)

unknown = attendance["att_score"].isna().sum()
show(f"Attendance rows with unknown status: {unknown}")
attendance["att_score"] = attendance["att_score"].fillna(0.0)

# Attendance % for every student and subject
att_summary = (
    attendance.groupby(["Student_ID", "Subject"])
    .agg(total_classes=("att_score", "count"), attended=("att_score", "sum"))
    .reset_index()
)
att_summary["Attendance_%"] = (
    att_summary["attended"] / att_summary["total_classes"] * 100
).round(1)

# ----------------------------------------------------------------------
# Step 3: Clean the performance data
# ----------------------------------------------------------------------
print("[3/6] Cleaning performance data...")

# Exam score: make it a number
performance["Exam_Score"] = pd.to_numeric(performance["Exam_Score"], errors="coerce")

# Homework %: values look like '100%', '90', '-5'. Remove '%' and make numeric.
performance["Homework_Completion_%"] = pd.to_numeric(
    performance["Homework_Completion_%"].str.replace("%", "", regex=False),
    errors="coerce",
)
# Negative homework % is impossible, so treat it as missing
bad_homework = (performance["Homework_Completion_%"] < 0).sum()
performance.loc[performance["Homework_Completion_%"] < 0, "Homework_Completion_%"] = np.nan
# Fill missing homework % with the median
median_hw = performance["Homework_Completion_%"].median()
performance["Homework_Completion_%"] = performance["Homework_Completion_%"].fillna(median_hw)
show(f"Invalid homework values replaced with median ({median_hw:.0f}): {bad_homework:,}")

# Exam score must be between 0 and 100. Anything else is an invalid entry.
total_before = len(performance)
invalid_scores = ~performance["Exam_Score"].between(0, 100)
show(f"Rows with exam score outside 0-100 (removed): {invalid_scores.sum():,}")
performance = performance[~invalid_scores].copy()

# ----------------------------------------------------------------------
# Step 4: Merge performance with attendance
# ----------------------------------------------------------------------
print("[4/6] Merging datasets...")
df = performance.merge(
    att_summary[["Student_ID", "Subject", "Attendance_%"]],
    on=["Student_ID", "Subject"],
    how="left",
)
missing_att = df["Attendance_%"].isna().sum()
show(f"Valid records after cleaning: {len(df):,} (from {total_before:,})")
show(f"Records without attendance data: {missing_att:,}")

# Grade for each exam score
def get_grade(score):
    if score >= 90:
        return "A (90-100)"
    elif score >= 75:
        return "B (75-89)"
    elif score >= 60:
        return "C (60-74)"
    return "D (below 60)"


df["Grade"] = df["Exam_Score"].apply(get_grade)

# Save the cleaned dataset
df.to_csv(os.path.join(OUTPUT_DIR, "cleaned_student_performance.csv"), index=False)

# ----------------------------------------------------------------------
# Step 5: Analysis
# ----------------------------------------------------------------------
print("[5/6] Analysing data...")
show("\n--- Exam scores ---")
show(f"Average score: {df['Exam_Score'].mean():.2f}")
show(f"Median score:  {df['Exam_Score'].median():.2f}")

show("\n--- Grade distribution ---")
grade_pct = (df["Grade"].value_counts(normalize=True) * 100).round(1).sort_index()
show(grade_pct.to_string())

show("\n--- Average score by subject ---")
subject_avg = df.groupby("Subject")["Exam_Score"].mean().round(2).sort_values()
show(subject_avg.to_string())

# Relationship between attendance, homework and exam score
valid_att = df.dropna(subset=["Attendance_%"])
corr_att = valid_att["Attendance_%"].corr(valid_att["Exam_Score"])
corr_hw = df["Homework_Completion_%"].corr(df["Exam_Score"])
show("\n--- Relationships (correlation, -1 to +1) ---")
show(f"Attendance % vs Exam score:  {corr_att:.4f}")
show(f"Homework %  vs Exam score:   {corr_hw:.4f}")
show("(A value close to 0 means there is no relationship.)")

# Average score for each attendance band
bands = pd.cut(
    valid_att["Attendance_%"],
    bins=[-1, 60, 75, 85, 100],
    labels=["Up to 60%", "60-75%", "75-85%", "85-100%"],
)
band_table = valid_att.groupby(bands, observed=True)["Exam_Score"].agg(["count", "mean"]).round(2)
show("\n--- Average score by attendance band ---")
show(band_table.to_string())

show("\n--- Average score by homework completion ---")
show(df.groupby("Homework_Completion_%")["Exam_Score"].agg(["count", "mean"]).round(2).to_string())

# ----------------------------------------------------------------------
# Step 6: Charts
# ----------------------------------------------------------------------
print("[6/6] Creating charts...")
plt.rcParams.update({"figure.dpi": 120, "axes.spines.top": False, "axes.spines.right": False})


def save_chart(name):
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, name), dpi=200)
    plt.close()


# Chart 1: Histogram - distribution of exam scores
plt.figure(figsize=(8, 5))
plt.hist(df["Exam_Score"], bins=20, color="#1f77b4", edgecolor="white")
plt.title("Distribution of Exam Scores", fontweight="bold")
plt.xlabel("Exam score")
plt.ylabel("Number of records")
save_chart("1_exam_score_histogram.png")

# Chart 2: Bar chart - average score by subject
plt.figure(figsize=(8, 5))
subject_order = df.groupby("Subject")["Exam_Score"].mean().sort_values(ascending=False)
bars = plt.bar(subject_order.index, subject_order.values, color="#2a9d8f")
plt.bar_label(bars, fmt="%.1f", padding=3)
plt.ylim(0, 100)
plt.title("Average Exam Score by Subject", fontweight="bold")
plt.ylabel("Average score")
save_chart("2_average_score_by_subject.png")

# Chart 3: Pie chart - grade distribution
plt.figure(figsize=(7, 7))
grade_counts = df["Grade"].value_counts().sort_index()
plt.pie(
    grade_counts,
    labels=grade_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=["#4caf50", "#8bc34a", "#ffc107", "#f44336"],
)
plt.title("Grade Distribution", fontweight="bold")
save_chart("3_grade_distribution_pie.png")

# Chart 4: Scatter plot - attendance vs exam score (random sample of 2000 points)
sample = valid_att.sample(n=min(2000, len(valid_att)), random_state=42)
plt.figure(figsize=(8, 5))
plt.scatter(sample["Attendance_%"], sample["Exam_Score"], alpha=0.35, color="#d62728", s=14)
slope, intercept = np.polyfit(valid_att["Attendance_%"], valid_att["Exam_Score"], 1)
x_line = np.array([0, 100])
plt.plot(x_line, slope * x_line + intercept, color="black", linewidth=2, label="Trend line")
plt.title(f"Attendance vs Exam Score (correlation = {corr_att:.3f})", fontweight="bold")
plt.xlabel("Attendance (%)")
plt.ylabel("Exam score")
plt.legend()
save_chart("4_attendance_vs_score_scatter.png")

# Chart 5: Bar chart - average score by attendance band
plt.figure(figsize=(8, 5))
bars = plt.bar(band_table.index.astype(str), band_table["mean"], color="#6a4c93")
plt.bar_label(bars, fmt="%.1f", padding=3)
plt.ylim(0, 100)
plt.title("Average Exam Score by Attendance Band", fontweight="bold")
plt.xlabel("Attendance band")
plt.ylabel("Average score")
save_chart("5_score_by_attendance_band.png")

# Save the text summary
with open(os.path.join(OUTPUT_DIR, "summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))

print("\nDone. Check the 'charts' and 'output' folders.")