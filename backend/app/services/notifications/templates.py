def shortlist_email(
    candidate_name: str,
    job_title: str,
    company_name: str,
    overall_score: float,
    strengths: list[str],
    scheduling_link: str | None,
) -> tuple[str, str]:
    subject = f"You've been shortlisted for {job_title} at {company_name}"

    strengths_html = "".join(f"<li>{s}</li>" for s in strengths[:5]) or "<li>Strong overall fit for the role</li>"

    scheduling_block = ""
    if scheduling_link:
        scheduling_block = f"""
        <p>The next step is a short interview. Please pick a time that works for you:</p>
        <p><a href="{scheduling_link}" style="display:inline-block;background:#4f46e5;color:#ffffff;
        padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:600;">
        Schedule Your Interview</a></p>
        """

    body = f"""
    <div style="font-family:sans-serif; color:#111827; max-width:560px;">
        <h2 style="color:#15803d;">Good news, {candidate_name}!</h2>
        <p>You've been shortlisted for the <strong>{job_title}</strong> role at
        <strong>{company_name}</strong>, with a match score of <strong>{overall_score}/100</strong>.</p>
        <p><strong>What stood out about your profile:</strong></p>
        <ul>{strengths_html}</ul>
        {scheduling_block}
        <p style="color:#6b7280; font-size:0.85rem; margin-top:24px;">
        This is an automated message from the {company_name} hiring pipeline.</p>
    </div>
    """
    return subject, body


def rejection_email(
    candidate_name: str,
    job_title: str,
    company_name: str,
    gaps: list[str],
) -> tuple[str, str]:
    subject = f"Update on your application for {job_title} at {company_name}"

    gaps_html = "".join(f"<li>{g}</li>" for g in gaps[:5])
    feedback_block = f"<p><strong>Areas that didn't fully align with this role:</strong></p><ul>{gaps_html}</ul>" if gaps else ""

    body = f"""
    <div style="font-family:sans-serif; color:#111827; max-width:560px;">
        <h2 style="color:#374151;">Thank you for applying, {candidate_name}</h2>
        <p>We appreciate you taking the time to apply for the <strong>{job_title}</strong> role at
        <strong>{company_name}</strong>. After careful review, we won't be moving forward with your
        application for this particular position.</p>
        {feedback_block}
        <p>We encourage you to apply for other roles that match your background in the future.</p>
        <p style="color:#6b7280; font-size:0.85rem; margin-top:24px;">
        This is an automated message from the {company_name} hiring pipeline.</p>
    </div>
    """
    return subject, body


def under_review_email(candidate_name: str, job_title: str, company_name: str, overall_score: float) -> tuple[str, str]:
    subject = f"Your application for {job_title} at {company_name} is under review"
    body = f"""
    <div style="font-family:sans-serif; color:#111827; max-width:560px;">
        <h2 style="color:#a16207;">Thanks for applying, {candidate_name}</h2>
        <p>Your application for the <strong>{job_title}</strong> role at <strong>{company_name}</strong>
        is currently under review (match score: {overall_score}/100). We'll follow up soon with next steps.</p>
        <p style="color:#6b7280; font-size:0.85rem; margin-top:24px;">
        This is an automated message from the {company_name} hiring pipeline.</p>
    </div>
    """
    return subject, body