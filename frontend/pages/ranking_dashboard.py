import os
import requests
import pandas as pd
import streamlit as st

from components.theme import missing_chips, page_header, skill_chips
from services.api_client import ApiError, get_job_rankings, list_jobs

page_header("Ranking Dashboard", "See candidates ranked by score for a job", emoji="🏆")

try:
    jobs = list_jobs(limit=200)
except ApiError as exc:
    st.error(f"Failed to load jobs: {exc.detail}")
    st.stop()
except Exception:
    st.error("Could not reach the backend API. Is it running?")
    st.stop()

if not jobs:
    st.warning("Create a job first.")
    st.stop()

job_options = {f"{j['title']} ({j['id'][:8]})": j["id"] for j in jobs}
job_label = st.selectbox("Select a Job", list(job_options.keys()))

if st.button("View Rankings", type="primary"):
    try:
        rankings = get_job_rankings(job_options[job_label])
    except ApiError as exc:
        st.error(f"Failed to load rankings ({exc.status_code}): {exc.detail}")
        st.stop()
    except Exception:
        st.error("Could not reach the backend API. Is it running?")
        st.stop()

    st.subheader(f"Rankings for {rankings['job_title']}")

    entries = rankings["rankings"]
    
    if not entries:
        st.info("No candidates have been screened for this job yet.")
    else:
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}
        for e in entries:
            with st.container(border=True):
                c1, c2, c3 = st.columns([0.6, 2.4, 1])
                rank_display = medal.get(e["rank"], f"#{e['rank']}")
                c1.markdown(f"### {rank_display}")
                with c2:
                    st.markdown(f"**{e['candidate_name']}**")
                    st.markdown(skill_chips(e["matched_skills"], limit=8), unsafe_allow_html=True)
                    if e["missing_skills"]:
                        st.caption("Missing:")
                        st.markdown(missing_chips(e["missing_skills"], limit=8), unsafe_allow_html=True)
                with c3:
                    st.progress(min(int(e["overall_score"]), 100) / 100, text=f"{e['overall_score']}/100")

        st.write("---")
        
        # 1. Convert the JSON list to a Pandas DataFrame
        df = pd.DataFrame(entries)
        
        # 2. Clean up the data format for the CSV
        df['matched_skills'] = df['matched_skills'].apply(lambda x: ", ".join(x))
        df['missing_skills'] = df['missing_skills'].apply(lambda x: ", ".join(x))
        
        # 3. Rename columns for the final report
        export_df = df.rename(columns={
            "rank": "Rank",
            "candidate_name": "Candidate Name",
            "overall_score": "Total Score",
            "matched_skills": "Matched Skills"
        })[['Rank', 'Candidate Name', 'Total Score', 'Matched Skills']]
        
        # 4. Generate the CSV bytes
        csv_data = export_df.to_csv(index=False).encode('utf-8')
        
        # 5. Fetch the PDF from the backend
        job_uuid = job_options[job_label]
        pdf_url = f"{os.environ.get('API_BASE_URL', 'http://localhost:8000')}/api/jobs/{job_uuid}/report/pdf"
        response = requests.get(pdf_url)

        # 6. Render the download buttons side-by-side
        st.write("**Export Shortlist**")
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            st.download_button(
                label="📥 Download Shortlist (CSV)",
                data=csv_data,
                file_name="shortlist_rankings.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with btn_col2:
            if response.status_code == 200:
                st.download_button(
                    label="📄 Download Report (PDF)",
                    data=response.content,
                    file_name="shortlist_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("⚠️ PDF generation endpoint not found or failed.")