import streamlit as st

from components.theme import missing_chips, page_header, skill_chips, status_chip
from services.api_client import ApiError, list_candidates, search_candidates, update_candidate_status

page_header("Candidates", "Search, filter, and manage your candidate pipeline", emoji="👥")

with st.expander("🔎 Search & Filter", expanded=True):
    col1, col2, col3 = st.columns(3)
    name = col1.text_input("Name contains")
    skill = col2.text_input("Skill")
    email = col3.text_input("Email contains")

    col4, col5, col6, col7 = st.columns(4)
    min_exp = col4.number_input("Min experience (yrs)", min_value=0.0, value=0.0, step=0.5)
    max_exp = col5.number_input("Max experience (yrs)", min_value=0.0, value=0.0, step=0.5)
    status_filter = col6.selectbox("Status", ["Any", "pending", "shortlisted", "rejected"])
    min_score = col7.number_input("Min score", min_value=0.0, max_value=100.0, value=0.0, step=5.0)

    col8, col9 = st.columns(2)
    sort_by = col8.selectbox("Sort by", ["Most Recent", "Highest Score", "Most Experience", "Name (A-Z)"])
    limit = col9.number_input("Results", min_value=5, max_value=200, value=30, step=5)

    search_clicked = st.button("Apply Filters", type="primary")

try:
    if search_clicked:
        data = search_candidates(
            name=name or None,
            email=email or None,
            skill=skill or None,
            min_experience=min_exp or None,
            max_experience=max_exp or None,
            status=None if status_filter == "Any" else status_filter,
            limit=int(limit),
        )
    else:
        data = list_candidates(limit=int(limit))
except ApiError as exc:
    st.error(f"Failed to load candidates: {exc.detail}")
    st.stop()
except Exception:
    st.error("Could not reach the backend API. Is it running?")
    st.stop()

items = data["items"]

if min_score:
    items = [c for c in items if (c.get("latest_score") or 0) >= min_score]

if sort_by == "Highest Score":
    items = sorted(items, key=lambda c: c.get("latest_score") or 0, reverse=True)
elif sort_by == "Most Experience":
    items = sorted(items, key=lambda c: c.get("total_experience_years") or 0, reverse=True)
elif sort_by == "Name (A-Z)":
    items = sorted(items, key=lambda c: c["name"].lower())

st.caption(f"Showing {len(items)} of {data['total']} candidates")

if "candidate_action_msg" in st.session_state:
    st.success(st.session_state.pop("candidate_action_msg"))

for candidate in items:
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([2.4, 1.6, 1.6, 1, 1.6])

        with c1:
            st.markdown(f"**👤 {candidate['name']}**")
            st.caption(f"📧 {candidate.get('email') or '—'}")
            st.code(candidate["id"], language=None)
            st.markdown(skill_chips(candidate.get("skills", [])), unsafe_allow_html=True)

        with c2:
            st.caption("💼 Last Screened Job")
            st.write(candidate.get("latest_job_title") or "Not yet screened")
            st.caption(f"Experience: {candidate.get('total_experience_years') or '—'} yrs")

        with c3:
            st.caption("⭐ Match Score")
            score = candidate.get("latest_score")
            if score is not None:
                st.progress(min(int(score), 100) / 100, text=f"{score}/100")
            else:
                st.write("—")

        with c4:
            st.markdown(status_chip(candidate.get("status", "pending")), unsafe_allow_html=True)

        with c5:
            st.caption("⚡ Actions")
            a1, a2, a3 = st.columns(3)
            candidate_id = candidate["id"]
            if a1.button("👁️", key=f"view_{candidate_id}", help="View details"):
                st.session_state["selected_candidate_id"] = candidate_id
                st.switch_page("pages/candidate_details.py")
            if a2.button("⭐", key=f"shortlist_{candidate_id}", help="Shortlist"):
                try:
                    update_candidate_status(candidate_id, "shortlisted")
                    st.session_state["candidate_action_msg"] = f"{candidate['name']} shortlisted."
                    st.rerun()
                except ApiError as exc:
                    st.error(f"Failed: {exc.detail}")
            if a3.button("❌", key=f"reject_{candidate_id}", help="Reject"):
                try:
                    update_candidate_status(candidate_id, "rejected")
                    st.session_state["candidate_action_msg"] = f"{candidate['name']} rejected."
                    st.rerun()
                except ApiError as exc:
                    st.error(f"Failed: {exc.detail}")
