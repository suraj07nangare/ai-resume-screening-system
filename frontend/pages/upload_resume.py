import streamlit as st

from components.theme import page_header
from services.api_client import ApiError, upload_resume

page_header("Upload Resume", "PDF or DOCX — scanned PDFs use OCR automatically", emoji="📄")

uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])

if uploaded_file is not None:
    if st.button("Process Resume", type="primary"):
        with st.spinner("Uploading and processing resume..."):
            try:
                result = upload_resume(uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
            except ApiError as exc:
                st.error(f"Upload failed ({exc.status_code}): {exc.detail}")
            except Exception:
                st.error("Could not reach the backend API. Is it running?")
            else:
                resume_file = result["resume_file"]
                candidate = result.get("candidate")

                if resume_file["extraction_status"] == "completed":
                    st.success(f"✅ Resume processed via **{resume_file['extraction_method']}** extraction.")
                else:
                    st.error(f"Extraction failed: {resume_file.get('error_message', 'Unknown error')}")

                with st.expander("Raw extraction details"):
                    st.json(resume_file)

                if candidate:
                    st.subheader("Candidate Created")
                    with st.container(border=True):
                        c1, c2 = st.columns(2)
                        c1.write(f"**Name:** {candidate['name']}")
                        c1.write(f"**Email:** {candidate.get('email') or '—'}")
                        c2.write(f"**Phone:** {candidate.get('phone') or '—'}")
                        c2.write(f"**Experience:** {candidate.get('total_experience_years') or '—'} years")
                        st.code(candidate["id"], language=None)
