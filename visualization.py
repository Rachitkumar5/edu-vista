
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "analyzed_student_data.csv"
OUTPUT_DIR = BASE_DIR / "visualizations"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load analyzed dataset
df = pd.read_csv(DATA_PATH)

# Professional chart style
sns.set_theme(style="whitegrid", palette="viridis")

subjects = [
    "mathematics",
    "physics",
    "computer_science",
    "english",
    "chemistry"
]

# 1. Grade Distribution
plt.figure(figsize=(9, 5))
sns.countplot(data=df, x="grade", order=["A+", "A", "B", "C", "D", "F"])
plt.title("Student Grade Distribution", fontsize=16)
plt.xlabel("Grade")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "grade_distribution.png", dpi=300)
plt.close()

# 2. Attendance vs Average Marks
plt.figure(figsize=(9, 5))
sns.scatterplot(
    data=df,
    x="attendance",
    y="average_marks",
    hue="grade",
    alpha=0.7
)
plt.title("Attendance vs Academic Performance", fontsize=16)
plt.xlabel("Attendance (%)")
plt.ylabel("Average Marks")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "attendance_vs_marks.png", dpi=300)
plt.close()

# 3. Average Subject Performance
subject_means = df[subjects].mean().sort_values(ascending=False)

plt.figure(figsize=(9, 5))
sns.barplot(x=subject_means.index, y=subject_means.values)
plt.title("Average Performance by Subject", fontsize=16)
plt.xlabel("Subject")
plt.ylabel("Average Marks")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "subject_performance.png", dpi=300)
plt.close()

# 4. Correlation Heatmap
plt.figure(figsize=(10, 7))
correlation = df[
    ["attendance", "study_hours", "average_marks"] + subjects
].corr()

sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)
plt.title("Student Performance Correlation Heatmap", fontsize=15)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "correlation_heatmap.png", dpi=300)
plt.close()

print("All visualizations generated successfully!")

for file in OUTPUT_DIR.iterdir():
    if file.suffix == ".png":
        print(f"Saved: {file.name}")
