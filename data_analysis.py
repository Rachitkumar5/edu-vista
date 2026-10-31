
import pandas as pd

# Load dataset
df = pd.read_csv("data/student_performance.csv")

print("=" * 50)
print("STUDENT PERFORMANCE ANALYTICS")
print("=" * 50)

# Basic information
print("\n1. Dataset Shape:")
print(df.shape)

print("\n2. First 5 Students:")
print(df.head())

print("\n3. Missing Values:")
print(df.isnull().sum())

print("\n4. Statistical Summary:")
print(df.describe())

# Calculate average marks
subjects = [
    "mathematics",
    "physics",
    "computer_science",
    "english",
    "chemistry"
]

df["average_marks"] = df[subjects].mean(axis=1)

# Assign grades
def calculate_grade(marks):
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"

df["grade"] = df["average_marks"].apply(calculate_grade)

# Display insights
print("\n5. Average Class Performance:")
print(df["average_marks"].mean())

print("\n6. Grade Distribution:")
print(df["grade"].value_counts())

print("\n7. Top 10 Students:")
print(
    df.nlargest(10, "average_marks")[
        ["name", "average_marks", "grade"]
    ]
)

# Save analyzed dataset
df.to_csv("data/analyzed_student_data.csv", index=False)

print("\nAnalysis completed successfully!")
