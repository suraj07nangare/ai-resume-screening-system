import streamlit as st

from components.theme import page_header, skill_chips
from services.api_client import ApiError, create_job

page_header("Create Job", "Paste a job description to extract structured requirements", emoji="💼")

with st.form("create_job_form"):
    title = st.text_input("Job Title")
    raw_description = st.text_area("Job Description", height=300)
    submitted = st.form_submit_button("Process Job Description", type="primary")

if submitted:
    if not title or not raw_description:
        st.warning("Please provide both a title and a description.")
    else:
        with st.spinner("Extracting job requirements..."):
            try:
                job = create_job(title, raw_description)
            except ApiError as exc:
                st.error(f"Failed to create job ({exc.status_code}): {exc.detail}")
            except Exception:
                st.error("Could not reach the backend API. Is it running?")
            else:
                st.success(f"✅ Job '{job['title']}' created.")
                with st.container(border=True):
                    st.write(f"**Job ID:** `{job['id']}`")
                    c1, c2 = st.columns(2)
                    c1.write(f"**Minimum Experience:** {job.get('minimum_experience_years') or '—'} years")
                    c2.write(f"**Education Requirement:** {job.get('education_requirement') or '—'}")

                    st.write("**Required Skills**")
                    st.markdown(skill_chips(job.get("required_skills", []), limit=20), unsafe_allow_html=True)
                    st.write("")
                    st.write("**Preferred Skills**")
                    st.markdown(skill_chips(job.get("preferred_skills", []), limit=20), unsafe_allow_html=True)
