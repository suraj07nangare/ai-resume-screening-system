import streamlit as st

from components.theme import page_header, skill_chips, status_chip
from services.api_client import ApiError, get_candidate

page_header("Candidate Details", "Full profile, skills, and screening history", emoji="🔎")

default_id = st.session_state.pop("selected_candidate_id", "")
candidate_id = st.text_input("Candidate ID", value=default_id)

if candidate_id:
    try:
        candidate = get_candidate(candidate_id)
    except ApiError as exc:
        st.error(f"Failed to load candidate ({exc.status_code}): {exc.detail}")
        st.stop()
    except Exception:
        st.error("Could not reach the backend API. Is it running?")
        st.stop()

    with st.container(border=True):
        top1, top2 = st.columns([3, 1])
        top1.header(candidate["name"])
        with top2:
            st.markdown(status_chip(candidate.get("status", "pending")), unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Email:** {candidate.get('email') or '—'}")
            st.write(f"**Phone:** {candidate.get('phone') or '—'}")
            st.write(f"**Experience:** {candidate.get('total_experience_years') or '—'} years")
        with col2:
            st.write(f"**Latest Score:** {candidate.get('latest_score') or 'Not yet screened'}")
            st.write(f"**Last Screened For:** {candidate.get('latest_job_title') or '—'}")
            st.write(f"**Education:** {candidate.get('education_summary') or '—'}")

        st.write("**Skills**")
        skill_names = [s["name"] for s in candidate.get("skills", [])]
        st.markdown(skill_chips(skill_names, limit=25), unsafe_allow_html=True)

        st.write("**Summary**")
        st.write(candidate.get("summary") or "No summary available")
