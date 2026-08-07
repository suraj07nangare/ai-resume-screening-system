import streamlit as st

from components.theme import missing_chips, page_header, skill_chips
from services.api_client import ApiError, create_screening, list_candidates, list_jobs

page_header("Screen Candidate", "Run an explainable match between a candidate and a job", emoji="🔍")

try:
    candidates = list_candidates(limit=200)["items"]
    jobs = list_jobs(limit=200)
except ApiError as exc:
    st.error(f"Failed to load data: {exc.detail}")
    st.stop()
except Exception:
    st.error("Could not reach the backend API. Is it running?")
    st.stop()

if not candidates or not jobs:
    st.warning("You need at least one candidate and one job before running a screening.")
    st.stop()

candidate_options = {f"{c['name']} ({c['id'][:8]})": c["id"] for c in candidates}
job_options = {f"{j['title']} ({j['id'][:8]})": j["id"] for j in jobs}

col1, col2 = st.columns(2)
candidate_label = col1.selectbox("Candidate", list(candidate_options.keys()))
job_label = col2.selectbox("Job", list(job_options.keys()))

if st.button("Run Screening", type="primary"):
    with st.spinner("Screening candidate..."):
        try:
            result = create_screening(candidate_options[candidate_label], job_options[job_label])
        except ApiError as exc:
            st.error(f"Screening failed ({exc.status_code}): {exc.detail}")
        except Exception:
            st.error("Could not reach the backend API. Is it running?")
        else:
            st.write("")
            st.progress(min(int(result["overall_score"]), 100) / 100, text=f"Overall Score: {result['overall_score']}/100")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Skills", result["skills_score"])
            c2.metric("Experience", result["experience_score"])
            c3.metric("Education", result["education_score"])
            c4.metric("Other", result["other_score"])

            st.write("")
            st.write("**✅ Matched Skills**")
            st.markdown(skill_chips(result["matched_skills"], limit=20), unsafe_allow_html=True)

            st.write("**🟡 Partial Matches**")
            st.markdown(skill_chips(result["partial_skills"], limit=20), unsafe_allow_html=True)

            st.write("**❌ Missing Skills**")
            st.markdown(missing_chips(result["missing_skills"], limit=20), unsafe_allow_html=True)

            with st.expander("Full Explanation"):
                st.text(result["explanation"])
