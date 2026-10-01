# Student Performance Analysis: Project Report

## 1. Project Overview
This project analyses student academic performance across six subjects (Math, Science, English, Arabic, History and Geography). It combines exam scores, homework completion and daily attendance records to look for patterns, and checks in particular whether attendance is related to exam scores.

## 2. Dataset
| File | Used for |
|---|---|
| `performance.csv` | Exam score and homework completion per student and subject (36,468 rows, about 11,580 students) |
| `attendance.csv` | Daily attendance status per student and subject (about 3.6 lakh rows) |
| `students.csv` | Student details |

## 3. Data Cleaning and Preprocessing
- **Attendance status** had inconsistent text, such as `PRESENT ` with a trailing space, ` late` with a leading space, lower-case `excused` and the typo `absnt`. All values were stripped of spaces and converted to lower case before scoring.
- **Attendance score rule:** Present = 1, Late or Excused = 0.5, and Absent, Left early or anything else = 0. Attendance % was calculated per student and subject. These weights are a project assumption, not part of the dataset.
- **Homework completion** mixed formats such as `100%` and `90`. The `%` sign was removed and every value converted to a number on a 0 to 100 scale. Invalid values (`-5`) were replaced with the median.
- **Exam scores above 100** (5,139 rows, about 14%) are not possible and were treated as invalid entries. They were excluded from the analysis, leaving **31,329 valid records**.
- **Missing attendance:** 205 of the valid records had no matching attendance data and were left out of the attendance analysis.

## 4. Key Findings

### Score distribution
The average exam score is **about 70 out of 100** (median 70). Grade split using A ≥ 90, B 75 to 89, C 60 to 74, D < 60:

| Grade | Share of records |
|---|---|
| A | 18.0% |
| B | 24.7% |
| C | 24.4% |
| D | 32.9% |

### Subject comparison
All six subjects have almost the same average, between **69.9 and 70.3**. No subject is noticeably stronger or weaker than the others.

### Attendance and exam scores
The correlation between attendance % and exam score is **about 0 (-0.001)**, and the same near-zero result appears in every subject. Average score by attendance band:

| Attendance band | Records | Average score |
|---|---|---|
| Up to 60% | 25,417 | 69.9 |
| 60 to 75% | 4,360 | 70.4 |
| 75 to 85% | 622 | 70.0 |
| 85 to 100% | 725 | 68.8 |

Higher attendance does **not** go with higher scores in this dataset. Attendance values are also low overall, with an average of about 44%, and over 90% of records fall below 75%.

### Homework completion and exam scores
The correlation between homework completion and exam score is also **about 0 (-0.001)**. Students at 80%, 90%, 95% and 100% completion all average about 70 marks.

## 5. Insights
1. **No relationship was found** between attendance and exam scores, or between homework completion and exam scores. The usual assumption that more attendance means better marks is not supported by this data.
2. **Performance is uniform across subjects**, so subject difficulty does not explain score differences.
3. **About one third of records (32.9%) fall in Grade D**, which is the largest group.
4. **Data quality is a concern.** Scores above 100, mixed text formats and invalid homework values suggest weak data entry controls.

## 6. Recommendations
- **Look for other factors.** Since attendance and homework do not explain scores here, collect other data such as study hours, teaching methods or prior results.
- **Support Grade D students.** With nearly one third of records below 60, targeted remedial classes are worth considering.
- **Improve data entry rules.** Restrict exam scores to 0 to 100 and use fixed attendance codes (Present, Absent, Late, Excused) to avoid typos and mixed formats.
- **Review attendance tracking.** The very low average attendance should be checked to confirm the records are accurate.

## 7. Limitations
- The relationship results apply only to this dataset. The near-zero correlations suggest the data may be synthetic or randomly generated, so real-world conclusions should not be drawn from it.
- Student and subject combinations with several records (about 14,000 rows) were not merged or removed.
- The attendance scoring weights (0.5 for Late and Excused) are assumptions and could change the attendance % values.

## 8. Tools Used
Python (Pandas, NumPy, Matplotlib, Seaborn), GitHub
