
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from textwrap import dedent

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="EDUVISTA | Student Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. CUSTOM CSS
# =====================================================

st.markdown(dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080d19;
    color: #f1f5f9;
}

[data-testid="stSidebar"] {
    background: #101827;
    border-right: 1px solid #263247;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #172236, #111a2b);
    border: 1px solid #293751;
    padding: 20px;
    border-radius: 16px;
}

[data-testid="stMetricLabel"] {
    color: #a5b4cc;
}

[data-testid="stMetricValue"] {
    color: #ffffff;
    font-weight: 800;
}

.hero {
    background: linear-gradient(120deg, #25245a, #172b50);
    border: 1px solid #354477;
    padding: 35px;
    border-radius: 18px;
    margin-bottom: 25px;
}

.hero-label {
    color: #a5b4fc;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}

.hero-title {
    color: white;
    font-size: 40px;
    font-weight: 800;
    margin-top: 12px;
}

.hero-subtitle {
    color: #cbd5e1;
    font-size: 14px;
    margin-top: 10px;
    line-height: 1.8;
}

.section-heading {
    color: #f1f5f9;
    font-size: 23px;
    font-weight: 800;
}

.stDownloadButton button {
    border-radius: 9px;
    font-weight: 600;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #263247;
    border-radius: 12px;
}
</style>
"""), unsafe_allow_html=True)

# =====================================================
# 3. LOAD DATASET
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

possible_files = [
    BASE_DIR / "data" / "analyzed_student_data.csv",
    BASE_DIR / "data" / "student_performance.csv"
]

DATA_FILE = next(
    (file for file in possible_files if file.exists()),
    None
)

if DATA_FILE is None:
    st.error("Dataset not found. Place your CSV inside the data folder.")
    st.stop()

df = pd.read_csv(DATA_FILE)
df.columns = [str(col).strip() for col in df.columns]

if df.empty:
    st.error("Your dataset is empty.")
    st.stop()

# =====================================================
# 4. DETECT DATASET COLUMNS
# =====================================================

def find_column(names):
    lookup = {
        col.lower().replace(" ", "_"): col
        for col in df.columns
    }

    for name in names:
        key = name.lower().replace(" ", "_")
        if key in lookup:
            return lookup[key]

    return None


student_col = find_column([
    "student_id", "student_name", "student", "name", "id"
])

class_col = find_column([
    "class", "class_name", "section", "course"
])

attendance_col = find_column([
    "attendance", "attendance_percentage",
    "attendance_percent"
])

study_col = find_column([
    "study_hours", "study_hour",
    "hours_studied", "daily_study_hours"
])

average_col = find_column([
    "average_marks", "avg_marks",
    "average", "overall_marks"
])

# Fallback columns

if student_col is None:
    df["Student"] = [
        f"Student_{i+1}" for i in range(len(df))
    ]
    student_col = "Student"

if class_col is None:
    df["Class"] = "General"
    class_col = "Class"

if attendance_col is None:
    df["Attendance"] = 0
    attendance_col = "Attendance"

if study_col is None:
    df["Study_Hours"] = 0
    study_col = "Study_Hours"

# Convert columns to numeric

for col in [attendance_col, study_col, average_col]:
    if col is not None:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Identify subject columns

excluded = {
    student_col,
    class_col,
    attendance_col,
    study_col,
    average_col
}

subject_cols = [
    col for col in df.select_dtypes(include=np.number).columns
    if col not in excluded
]

# Calculate average marks

if subject_cols:
    df["Calculated_Average"] = df[subject_cols].mean(axis=1)
    marks_col = "Calculated_Average"

elif average_col:
    marks_col = average_col

else:
    st.error("No marks columns found in your dataset.")
    st.stop()

df[marks_col] = (
    df[marks_col]
    .fillna(0)
    .clip(0, 100)
)

df[attendance_col] = (
    df[attendance_col]
    .fillna(0)
    .clip(0, 100)
)

df[study_col] = df[study_col].fillna(0)

# =====================================================
# 5. GRADE CALCULATION
# =====================================================

def calculate_grade(mark):
    if mark >= 90:
        return "A+"
    elif mark >= 80:
        return "A"
    elif mark >= 70:
        return "B"
    elif mark >= 60:
        return "C"
    elif mark >= 40:
        return "D"
    return "F"


df["Dashboard_Grade"] = df[marks_col].apply(calculate_grade)

# =====================================================
# 6. SIDEBAR
# =====================================================

st.sidebar.markdown("# 🎓 EDUVISTA")
st.sidebar.caption("STUDENT INTELLIGENCE PLATFORM")
st.sidebar.divider()

st.sidebar.subheader("Dashboard Filters")

classes = sorted(
    df[class_col].dropna().astype(str).unique()
)

selected_classes = st.sidebar.multiselect(
    "Select Class",
    classes,
    default=classes
)

grades = ["A+", "A", "B", "C", "D", "F"]

selected_grades = st.sidebar.multiselect(
    "Select Grade",
    grades,
    default=grades
)

attendance_range = st.sidebar.slider(
    "Attendance Range",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

search_student = st.sidebar.text_input(
    "Search Student",
    placeholder="Enter student name or ID"
)

st.sidebar.divider()
st.sidebar.caption("POWERED BY PYTHON + STREAMLIT")
st.sidebar.caption("EDUVISTA ANALYTICS • 2026")

# =====================================================
# 7. FILTER DATA
# =====================================================

filtered = df[
    df[class_col].astype(str).isin(selected_classes)
    & df["Dashboard_Grade"].isin(selected_grades)
    & df[attendance_col].between(
        attendance_range[0],
        attendance_range[1]
    )
].copy()

filtered = filtered[
    filtered[student_col].astype(str).str.contains(
        search_student,
        case=False,
        na=False
    )
]

# =====================================================
# 8. MAIN HERO SECTION
# =====================================================

st.markdown(dedent("""
<div class="hero">
    <div class="hero-label">
        ACADEMIC INTELLIGENCE • PERFORMANCE ANALYTICS
    </div>
    <div class="hero-title">
        EDUVISTA
    </div>
    <div class="hero-subtitle">
        Student Intelligence & Performance Analytics
        <br>
        Monitor academic performance, explore student progress
        and discover meaningful insights.
    </div>
</div>
"""), unsafe_allow_html=True)

if filtered.empty:
    st.warning("No students match the selected filters. Change your filters.")
    st.stop()

# =====================================================
# 9. KPI CARDS
# =====================================================

total_students = len(filtered)
average_marks = filtered[marks_col].mean()
average_attendance = filtered[attendance_col].mean()
average_study = filtered[study_col].mean()

k1, k2, k3, k4 = st.columns(4)

k1.metric("TOTAL STUDENTS", f"{total_students:,}")
k2.metric("AVERAGE MARKS", f"{average_marks:.2f}", "Out of 100")
k3.metric("ATTENDANCE", f"{average_attendance:.1f}%")
k4.metric("STUDY HOURS", f"{average_study:.1f} hrs")

st.divider()

# =====================================================
# 10. DASHBOARD TABS
# =====================================================

overview, students_tab, insights_tab = st.tabs([
    "📊 Overview",
    "🏆 Students",
    "💡 Insights"
])

# =====================================================
# 11. OVERVIEW TAB
# =====================================================

with overview:

    left, right = st.columns(2)

    # Grade distribution

    with left:
        st.subheader("Grade Distribution")

        grade_order = ["A+", "A", "B", "C", "D", "F"]

        grade_counts = (
            filtered["Dashboard_Grade"]
            .value_counts()
            .reindex(grade_order, fill_value=0)
            .reset_index()
        )

        grade_counts.columns = ["Grade", "Students"]

        fig = px.bar(
            grade_counts,
            x="Grade",
            y="Students",
            color="Grade",
            text="Students",
            color_discrete_sequence=[
                "#a78bfa", "#60a5fa", "#818cf8",
                "#fbbf24", "#fb923c", "#f87171"
            ]
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )

        st.plotly_chart(fig, width="stretch")

    # Subject performance

    with right:
        st.subheader("Subject Performance")

        if subject_cols:
            subject_data = pd.DataFrame({
                "Subject": subject_cols,
                "Average Marks": [
                    filtered[col].mean()
                    for col in subject_cols
                ]
            })

            fig = px.bar(
                subject_data,
                x="Subject",
                y="Average Marks",
                color="Average Marks",
                text_auto=".1f",
                color_continuous_scale="Purples"
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False
            )

            st.plotly_chart(fig, width="stretch")

        else:
            st.info("Subject-wise marks are not available.")

    # Attendance vs marks

    st.subheader("Attendance vs Academic Performance")

    fig = px.scatter(
        filtered,
        x=attendance_col,
        y=marks_col,
        color="Dashboard_Grade",
        hover_name=student_col,
        size=study_col if filtered[study_col].max() > 0 else None,
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={
            attendance_col: "Attendance (%)",
            marks_col: "Average Marks"
        }
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, width="stretch")

# =====================================================
# 12. STUDENTS TAB
# =====================================================

with students_tab:

    st.subheader("🏆 Student Leaderboard")

    leaderboard = filtered.sort_values(
        marks_col,
        ascending=False
    ).copy()

    leaderboard.insert(
        0,
        "Rank",
        range(1, len(leaderboard) + 1)
    )

    display_cols = [
        "Rank",
        student_col,
        class_col,
        marks_col,
        attendance_col,
        study_col,
        "Dashboard_Grade"
    ]

    leaderboard_display = leaderboard[
        display_cols
    ].rename(columns={
        marks_col: "Average Marks",
        attendance_col: "Attendance (%)",
        study_col: "Study Hours",
        "Dashboard_Grade": "Grade"
    })

    st.dataframe(
        leaderboard_display,
        width="stretch",
        hide_index=True
    )

    st.divider()
    st.subheader("🔍 Individual Student Explorer")

    selected_student = st.selectbox(
        "Choose a student",
        filtered[student_col].astype(str).tolist()
    )

    student_data = filtered[
        filtered[student_col].astype(str) == selected_student
    ].iloc[0]

    st.markdown(f"### {selected_student}")

    a, b, c = st.columns(3)

    a.metric("Average Marks", f"{student_data[marks_col]:.1f}/100")
    b.metric("Attendance", f"{student_data[attendance_col]:.1f}%")
    c.metric("Grade", student_data["Dashboard_Grade"])

    if subject_cols:
        st.subheader("Subject-wise Marks")

        scores = pd.DataFrame({
            "Subject": subject_cols,
            "Marks": [
                student_data[col]
                for col in subject_cols
            ]
        })

        fig = px.bar(
            scores,
            x="Subject",
            y="Marks",
            color="Marks",
            text_auto=".1f",
            color_continuous_scale="Purples"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, width="stretch")

# =====================================================
# 13. INSIGHTS TAB
# =====================================================

with insights_tab:

    st.subheader("💡 Academic Insights")

    top_student = filtered.loc[filtered[marks_col].idxmax()]
    low_student = filtered.loc[filtered[marks_col].idxmin()]

    high_attendance = (
        filtered[attendance_col] >= 75
    ).sum()

    low_attendance = (
        filtered[attendance_col] < 75
    ).sum()

    at_risk = filtered[
        (filtered[marks_col] < 40)
        | (filtered[attendance_col] < 75)
    ]

    c1, c2 = st.columns(2)

    with c1:
        st.success(
            f"🏆 Top Performer: **{top_student[student_col]}** "
            f"with {top_student[marks_col]:.1f} marks."
        )

        st.info(
            f"📚 {high_attendance} students have attendance "
            f"of 75% or above."
        )

    with c2:
        st.warning(
            f"⚠️ Students needing attention: **{len(at_risk)}** "
            f"based on low marks or attendance."
        )

        st.info(
            f"📉 {low_attendance} students have attendance below 75%."
        )

    st.subheader("Students Requiring Attention")

    if len(at_risk) > 0:
        st.dataframe(
            at_risk[
                [
                    student_col,
                    marks_col,
                    attendance_col,
                    "Dashboard_Grade"
                ]
            ].rename(columns={
                marks_col: "Average Marks",
                attendance_col: "Attendance (%)",
                "Dashboard_Grade": "Grade"
            }),
            width="stretch",
            hide_index=True
        )
    else:
        st.success("No students currently meet the at-risk criteria.")

    st.subheader("Performance Summary")

    st.write(
        f"The filtered dataset contains **{total_students} students**. "
        f"The average academic score is **{average_marks:.2f}/100**, "
        f"with average attendance of **{average_attendance:.1f}%**."
    )

# =====================================================
# 14. DOWNLOAD REPORT
# =====================================================

st.divider()
st.subheader("📥 Download Reports")

csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download EDUVISTA Student Report",
    data=csv_data,
    file_name="EDUVISTA_student_performance_report.csv",
    mime="text/csv",
    width="stretch"
)

# =====================================================
# 15. FOOTER
# =====================================================

st.divider()

st.markdown(dedent("""
<div style="text-align:center; padding:20px; color:#94a3b8;">
    <h2 style="color:#a5b4fc;">🎓 EDUVISTA</h2>
    <p>Student Intelligence & Performance Analytics</p>
    <small>
        Built with Python • Pandas • NumPy • Plotly • Streamlit
    </small>
    <br><br>
    <small>© 2026 EDUVISTA. All rights reserved.</small>
</div>
"""), unsafe_allow_html=True)

# =====================================================
# 3. DATA UPLOAD SYSTEM
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

st.sidebar.divider()
st.sidebar.subheader("📂 Upload Your Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"],
    help="Upload your own student performance dataset."
)

if uploaded_file is not None:

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.sidebar.success("Dataset uploaded successfully!")

    except Exception as e:
        st.error(f"Unable to read file: {e}")
        st.stop()

else:

    possible_files = [
        BASE_DIR / "data" / "analyzed_student_data.csv",
        BASE_DIR / "data" / "student_performance.csv"
    ]

    DATA_FILE = next(
        (file for file in possible_files if file.exists()),
        None
    )

    if DATA_FILE is None:
        st.info("Upload a CSV or Excel dataset to begin.")
        st.stop()

    df = pd.read_csv(DATA_FILE)

df.columns = [str(col).strip() for col in df.columns]

if df.empty:
    st.error("The uploaded dataset is empty.")
    st.stop()

st.subheader("📋 Dataset Preview")

st.write(f"**Rows:** {len(df)} | **Columns:** {len(df.columns)}")

st.dataframe(
    df.head(10),
    width="stretch",
    hide_index=True
)
