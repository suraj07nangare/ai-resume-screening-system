from collections import Counter

import pandas as pd
import streamlit as st

from components.theme import kpi_card, page_header, status_chip
from services.api_client import ApiError, get_health, list_candidates, list_jobs

page_header("Dashboard", "Live recruitment metrics from your data", emoji="📊")

try:
    health = get_health()
    st.success(f"Backend connected — status: {health['status']} ({health['app_env']})")
except ApiError as exc:
    st.error(f"Backend unavailable: {exc.detail}")
except Exception:
    st.error("Could not reach the backend API. Is it running?")

try:
    candidates = list_candidates(limit=200)
    jobs = list_jobs(limit=200)
except ApiError as exc:
    st.error(f"Failed to load dashboard data: {exc.detail}")
    st.stop()
except Exception:
    st.error("Could not reach the backend API. Is it running?")
    st.stop()

candidate_items = candidates["items"]
scored = [c for c in candidate_items if c.get("latest_score") is not None]
avg_score = round(sum(c["latest_score"] for c in scored) / len(scored), 1) if scored else None

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(kpi_card("Candidates", str(candidates["total"] or len(candidate_items)), "👥"), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_card("Jobs", str(len(jobs)), "💼"), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card("Screenings", str(len(scored)), "📝"), unsafe_allow_html=True)
with col4:
    st.markdown(kpi_card("Avg Score", f"{avg_score}" if avg_score is not None else "—", "⭐"), unsafe_allow_html=True)

st.write("")
st.write("")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Score Distribution")
    if scored:
        buckets = ["0-20", "21-40", "41-60", "61-80", "81-100"]
        counts = [0, 0, 0, 0, 0]
        for c in scored:
            s = c["latest_score"]
            idx = min(int(s // 20), 4)
            counts[idx] += 1
        df = pd.DataFrame({"Score Range": buckets, "Candidates": counts}).set_index("Score Range")
        st.bar_chart(df, use_container_width=True)
    else:
        st.info("Run some screenings to see score distribution.")

with col_right:
    st.subheader("Top Skills Across Candidates")
    skill_counter = Counter()
    for c in candidate_items:
        skill_counter.update(c.get("skills", []))
    if skill_counter:
        top_skills = skill_counter.most_common(8)
        df = pd.DataFrame(top_skills, columns=["Skill", "Candidates"]).set_index("Skill")
        st.bar_chart(df, use_container_width=True)
    else:
        st.info("Upload resumes to see skill trends.")

st.write("")
st.subheader("🏆 Top Candidates")
top = sorted(scored, key=lambda c: c["latest_score"], reverse=True)[:5]
if top:
    for c in top:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.markdown(f"**{c['name']}**  \n{c.get('email') or '—'}")
            c2.markdown(status_chip(c.get("status", "pending")), unsafe_allow_html=True)
            c3.metric("Score", c["latest_score"])
else:
    st.info("No screenings have been run yet.")

st.write("")
st.subheader("🕓 Recent Candidates")
recent = candidate_items[:5]
if recent:
    for c in recent:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.markdown(f"**{c['name']}**  \nExperience: {c.get('total_experience_years') or '—'} yrs")
            c2.markdown(", ".join(c.get("skills", [])[:4]) or "—")
            c3.markdown(status_chip(c.get("status", "pending")), unsafe_allow_html=True)
else:
    st.info("No candidates yet. Upload a resume to get started.")
