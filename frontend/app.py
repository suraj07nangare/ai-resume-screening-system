import streamlit as st

from components.theme import apply_theme

st.set_page_config(page_title="AI Resume Screener", page_icon="🤖", layout="wide")
apply_theme()

navigation = st.navigation(
    [
        st.Page("pages/dashboard.py", title="Dashboard", icon="📊", default=True),
        st.Page("pages/upload_resume.py", title="Upload Resume", icon="📄"),
        st.Page("pages/create_job.py", title="Create Job", icon="💼"),
        st.Page("pages/candidates.py", title="Candidates", icon="👥"),
        st.Page("pages/screen_candidate.py", title="Screen Candidate", icon="🔍"),
        st.Page("pages/ranking_dashboard.py", title="Ranking Dashboard", icon="🏆"),
        st.Page("pages/candidate_details.py", title="Candidate Details", icon="🔎"),
    ]
)

navigation.run()
