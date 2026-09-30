import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("[1/4] Loading datasets...")
students = pd.read_csv('students.csv')
attendance = pd.read_csv('attendance.csv')
performance = pd.read_csv('performance.csv')

print("[2/4] Processing attendance records...")
attendance['clean_status'] = attendance['Attendance_Status'].astype(str).str.strip().str.lower()

def score_attendance(status):
    if 'present' in status:
        return 1.0
    elif 'late' in status or 'excused' in status:
        return 0.5
    return 0.0

attendance['att_score'] = attendance['clean_status'].apply(score_attendance)

att_summary = attendance.groupby(['Student_ID', 'Subject']).agg(
    total_classes=('att_score', 'count'),
    attended_score=('att_score', 'sum')
).reset_index()

att_summary['Attendance_%'] = (att_summary['attended_score'] / att_summary['total_classes']) * 100
att_summary['Attendance_%'] = att_summary['Attendance_%'].round(1)

print("[3/4] Cleaning performance records and merging data...")
df = pd.merge(performance, att_summary[['Student_ID', 'Subject', 'Attendance_%']], on=['Student_ID', 'Subject'], how='left')

# Sanitize Homework Completion column
df['Homework_Completion_%'] = df['Homework_Completion_%'].astype(str).str.replace('%', '', regex=False)
df['Homework_Completion_%'] = pd.to_numeric(df['Homework_Completion_%'], errors='coerce')
df['Homework_Completion_%'] = df['Homework_Completion_%'].apply(
    lambda x: np.nan if x < 0 else (x * 100 if x <= 1.0 else x)
)
df['Homework_Completion_%'] = df['Homework_Completion_%'].fillna(df['Homework_Completion_%'].median())

# Export Cleaned Master Dataset
df.to_csv('cleaned_student_performance.csv', index=False)
print(" -> Exported: cleaned_student_performance.csv")

print("[4/4] Generating visual charts...")
os.makedirs('charts', exist_ok=True)
sns.set_theme(style="whitegrid")
plt.figure(figsize=(15, 12))

# Chart 1: Histogram - Exam Score Distribution
plt.subplot(2, 2, 1)
sns.histplot(df['Exam_Score'], kde=True, bins=25, color='#1f77b4')
plt.title('Distribution of Exam Scores', fontsize=12, fontweight='bold')
plt.xlabel('Exam Score')
plt.ylabel('Student Count')

# Chart 2: Bar Chart - Subject vs Average Score
plt.subplot(2, 2, 2)
subject_avg = df.groupby('Subject')['Exam_Score'].mean().reset_index()
sns.barplot(data=subject_avg, x='Subject', y='Exam_Score', palette='mako')
plt.title('Average Exam Score by Subject', fontsize=12, fontweight='bold')
plt.ylim(0, 100)

# Chart 3: Pie Chart - Grade Distribution
plt.subplot(2, 2, 3)
def get_grade(score):
    if score >= 90: return 'Grade A (>=90)'
    elif score >= 75: return 'Grade B (75-89)'
    elif score >= 60: return 'Grade C (60-74)'
    else: return 'Grade D (<60)'

df['Grade'] = df['Exam_Score'].apply(get_grade)
grade_counts = df['Grade'].value_counts()
plt.pie(grade_counts, labels=grade_counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
plt.title('Student Grade Distribution', fontsize=12, fontweight='bold')

# Chart 4: Scatter Plot - Attendance vs Exam Score
plt.subplot(2, 2, 4)
sample_df = df.sample(n=min(1500, len(df)), random_state=42)
sns.scatterplot(data=sample_df, x='Attendance_%', y='Exam_Score', alpha=0.5, color='#d62728')
sns.regplot(data=sample_df, x='Attendance_%', y='Exam_Score', scatter=False, color='#333333')
plt.title('Attendance vs. Exam Score Correlation', fontsize=12, fontweight='bold')
plt.xlabel('Attendance (%)')
plt.ylabel('Exam Score')

plt.tight_layout()
plt.savefig('charts/student_performance_charts.png', dpi=300)
print(" -> Saved: charts/student_performance_charts.png")
print("\nExecution Completed Successfully.")